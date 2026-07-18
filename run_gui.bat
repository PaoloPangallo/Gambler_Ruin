@echo off
:: Imposta la codifica UTF-8 per supportare caratteri speciali nel terminale
chcp 65001 >nul
title Rovina del Giocatore - Interfaccia Grafica
color 0b

echo ======================================================================
echo           ROVINA DEL GIOCATORE - SIMULAZIONE DTMC (GUI)
echo ======================================================================
echo  [INFO] Avvio dell'interfaccia grafica interattiva in corso...
echo  [INFO] Utilizzo dell'ambiente 'uv' per la gestione automatica...
echo.

:: Esegue la GUI tramite uv
uv run src/gui.py

:: Controlla se ci sono stati errori durante l'avvio
if %errorlevel% neq 0 (
    color 0c
    echo.
    echo [ERRORE] Impossibile avviare la GUI. 
    echo Assicurati che 'uv' sia installato correttamente nel tuo sistema.
    echo.
    pause
)
