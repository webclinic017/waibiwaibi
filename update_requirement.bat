@echo off
activate stock && pip list --format=freeze > requirements.txt && conda env export > environment.yaml

