@echo off
activate stock && pip freeze > requirements.txt && conda env export > environment.yaml

