from app.modules.topology_optimization.topology_optimization_module import TopologyOptimizationModule
import numpy as np

from app.modules.utils.traffic_utils import TrafficUtils

class TopologyOptimizationModuleImpl(TopologyOptimizationModule):

    def _ttf(vectorC0, vectorX0, g0):
        value = 0
        for counter1 in range(len(g0)):
            value = value + (g0[counter1, 2] + 0.15 * ((vectorX0[g0[counter1][0]][g0[counter1][1]]/vectorC0[g0[counter1][0]][g0[counter1][1]]) ** 4))
        return value
    
    def _icf(vectorC0, lowerBound0 ,g0):
        value = 0
        for counter1 in range(len(g0)):
            value = value + 0.000001 * ((vectorC0[g0[counter1][0]][g0[counter1][1]] - lowerBound0[g0[counter1][0]][g0[counter1][1]]) ** 2)
        return value

    def get_topology(self, input):
        ## Исходные данные
        lowerBound = input[1]
        upperBound = input[2]
        d = input[3]
        t0 = input[4]
        g = input[5]
        e00 = 0.01

        ## Инициализация переменных верхнего уровня
        upperLevel =  np.zeros(len(lowerBound), len(lowerBound))
        for i in range(len(lowerBound)):
            for j in range(len(lowerBound)):
                upperLevel[i][j] = np.random(lowerBound[i,j],upperBound[i,j])
            
        lowerLevelX0 = TrafficUtils.leblanc(t0,d,upperLevel, e00,g)
        # Предполагаем, что массив g уже задан как numpy массив
        vecC = []
        vecX0 = []
        vecX1 = []

        result = g.T[0:2].T

        # Добавляем результат в каждый из списков
        vecC.append(result)
        vecX0.append(result)
        vecX1.append(result)

        Fystart = self._ttf[upperLevel, lowerLevelX0, g] + self._icf[upperLevel , lowerBound, d, g]

        for i in range(len(vecC)):
            vecC[0][i].append(upperLevel[vecC[0][i][0]][vecC[0][i][1]])
            vecX0[0][i].append(lowerLevelX0[vecC[0][i][0]][vecX0[0][i][1]])
    
        ## Вычисление Якобиана
        eps = 1.0
        jacobi = 0

        while np.sum(jacobi) == 0:
            jacobi = []
            
            for i in range(len(vecC[0])):
                # Создаем копию upperLevelVariable с модифицированным элементом
                epsUpperLevelVariable = upperLevel.copy()
                row = vecC[0][i][0] - 1  # Переход к 0-based индексации
                col = vecC[0][i][1] - 1
                val = vecC[0][i][2]
                
                epsUpperLevelVariable[row, col] = val + eps
                
                # Проверка границ
                if epsUpperLevelVariable[row, col] > upperBound[row, col]:
                    epsUpperLevelVariable[row, col] = upperBound[row, col]
                elif epsUpperLevelVariable[row, col] < lowerBound[row, col]:
                    epsUpperLevelVariable[row, col] = lowerBound[row, col]
                
                # Вычисление lowerLevelVariableX1
                lowerLevelVariableX1 = TrafficUtils.leBlanc(t0, d, epsUpperLevelVariable, e00, g)
                
                # Создание vecX1
                vecX1 = [g[:, :2].copy()]  # Берем первые два столбца g
                
                for ii in range(len(vecC[0])):
                    row_x1 = vecX1[0][ii][0] - 1
                    col_x1 = vecX1[0][ii][1] - 1
                    vecX1[0][ii] = np.append(vecX1[0][ii], lowerLevelVariableX1[row_x1, col_x1])
                
                # Вычисление якобиана
                jacobi_col = (vecX1[0][:, 2] - vecX0[0][:, 2]) / eps
                jacobi.append(jacobi_col)
            
            eps += 0.5

            jacobi_array = np.array(jacobi)


            def x(y):
                Y = y.copy()  # Создаем копию входного массива
                # (Transpose@vecX0[[1]])[[3]] - третья колонка транспонированного vecX0[0]
                vecX0_col3 = vecX0[0][:, 2]  # Третья колонка (индекс 2 для 0-based)
                
                # (Transpose@vecC[[1]])[[3]] - третья колонка транспонированного vecC[0]
                vecC_col3 = vecC[0][:, 2]  # Третья колонка
                
                # Вычисляем результат: vecX0_col3 + jacobi.(Y - vecC_col3)
                # Предполагаем, что jacobi - это numpy массив
                result = vecX0_col3 + jacobi_array @ (Y - vecC_col3)
                
                return result
            

