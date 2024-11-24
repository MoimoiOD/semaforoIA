from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import pickle
import json
import numpy as np

app = FastAPI()

# Modelo para armazenar dados de horários de pico
class PeakHourData(BaseModel):
    signal_id: int                  # ID do sinal
    peak_hours: List[str]           # Lista de horários de pico no formato "HH:MM-HH:MM"

# Modelo para os dados de cálculo de tempos
class SignalData(BaseModel):
    quantity: int                   # Quantidade de carros no sinal
    rate: float                     # Taxa de carros que passam por segundo
    signal_id: int                  # ID do sinal

class CycleData(BaseModel):
    total_cycle_time: float         # Tempo total do ciclo
    signals: List[SignalData]       # Lista de dados para cada sinal

# Carregar o modelo de IA pré-treinado
try:
    with open("model.pkl", "rb") as file:
        model = pickle.load(file)
except FileNotFoundError:
    model = None

# Rota para registrar horários de pico e salvar no TXT
@app.post("/register-peak-hours/")
def register_peak_hours(data: List[PeakHourData]):
    try:
        with open("peak_hours.txt", "w") as file:
            for entry in data:
                file.write(json.dumps(entry.dict()) + "\n")
        return {"message": "Horários de pico registrados com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar os dados: {str(e)}")

# Rota para calcular os tempos considerando IA
@app.post("/calculate-times/")
def calculate_times(data: CycleData):
    if model is None:
        raise HTTPException(status_code=500, detail="Modelo de IA não está carregado.")

    try:
        # Lê os horários de pico do arquivo
        peak_hours = {}
        with open("peak_hours.txt", "r") as file:
            for line in file:
                entry = json.loads(line.strip())
                peak_hours[entry["signal_id"]] = entry["peak_hours"]

        # Identifica o horário atual
        current_time = datetime.now().strftime("%H:%M")

        # Calcula a demanda normalizada para cada sinal
        normalized_demands = []
        for signal in data.signals:
            is_peak = any(
                check_time_in_range(current_time, peak_range)
                for peak_range in peak_hours.get(signal.signal_id, [])
            )

            # Ajusta a quantidade de carros no horário de pico (aplica peso maior)
            quantity = signal.quantity * (1.5 if is_peak else 1.0)
            normalized_demand = quantity / signal.rate
            normalized_demands.append(normalized_demand)

        # Soma total da demanda normalizada
        total_normalized_demand = sum(normalized_demands)

        # Calcula o tempo de cada sinal
        signal_times = [
            {
                "signal_id": signal.signal_id,
                "time": round((demand / total_normalized_demand) * data.total_cycle_time, 2)
            }
            for signal, demand in zip(data.signals, normalized_demands)
        ]

        return {"total_cycle_time": data.total_cycle_time, "signal_times": signal_times}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao calcular os tempos: {str(e)}")

# Função auxiliar para verificar se o horário atual está no intervalo de pico
def check_time_in_range(current_time: str, peak_range: str) -> bool:
    try:
        start, end = peak_range.split("-")
        current_time = datetime.strptime(current_time, "%H:%M")
        start_time = datetime.strptime(start, "%H:%M")
        end_time = datetime.strptime(end, "%H:%M")
        return start_time <= current_time <= end_time
    except Exception:
        return False
