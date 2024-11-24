import pickle
from sklearn.linear_model import LinearRegression
import numpy as np

# Dados fictícios para treino
# [quantidade de carros, taxa de fluxo, horário de pico (1 ou 0), tempo total do ciclo]
X = np.array([
    [20, 2, 0, 120],
    [50, 3, 1, 120],
    [30, 2, 0, 120],
    [40, 4, 1, 120]
])
# Tempos ideais correspondentes
y = np.array([20, 40, 30, 30])

# Treinar o modelo
model = LinearRegression()
model.fit(X, y)

# Salvar o modelo
with open("model.pkl", "wb") as file:
    pickle.dump(model, file)

print("Modelo treinado e salvo!")
