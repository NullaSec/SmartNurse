#!/usr/bin/env python3
from decision_trees import MedicalDecisionTree
from singlestore_client import SingleStoreMed
from ai_enhancer import AIEnhancer
import os
import time
import sys
from dotenv import load_dotenv

# Configuração inicial
load_dotenv()

def clear_screen():
    """Limpa o terminal de forma multiplataforma"""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_banner():
    """Exibe o banner do sistema"""
    clear_screen()
    print("""
    ╔══════════════════════════════════════════╗
    ║   SISTEMA DE TRIAGEM MÉDICA AVANÇADA     ║
    ╠══════════════════════════════════════════╣
    ║  Combina:                                ║
    ║  • Árvores de decisão clínica            ║
    ║  • Protocolos médicos (SingleStore)      ║
    ║  • IA generativa (Gemini 1.5 Flash)      ║
    ╚══════════════════════════════════════════╝
    """)

def get_user_input():
    """Obtém e valida entrada do usuário"""
    print("\n" + "═"*50)
    print("ℹ️  Descreva seus sintomas principais (ex: 'dor de cabeça intensa com náuseas')")
    symptoms = input("> Sintomas: ").strip()
    
    while len(symptoms.split()) < 3:
        print("⚠️  Por favor, forneça mais detalhes (mínimo 3 palavras)")
        symptoms = input("> Sintomas: ").strip()

    print("\nℹ️  Histórico médico relevante (deixe em branco se não souber)")
    history = input("> Histórico: ").strip() or "Não informado"

    print("\nℹ️  Idade (digite 0 se não quiser informar)")
    while True:
        try:
            age = int(input("> Idade: ") or "0")
            break
        except ValueError:
            print("⚠️  Por favor, digite um número válido")

    return symptoms, history, age

def display_results(diagnosis, guidelines, ai_response):
    """Mostra os resultados formatados"""
    print("\n" + "═"*50)
    print("🔍 RESULTADOS DA TRIAGEM")
    print("═"*50)
    
    # Diagnóstico
    print(f"\n📌 Categoria: {diagnosis['categoria'].upper()}")
    print(f"🚨 Nível de Urgência: {diagnosis['urgencia']}")
    
    if diagnosis['alertas']:
        print("\n⚠️  ALERTAS CLÍNICOS:")
        for alert in diagnosis['alertas']:
            print(f"    • {alert}")
    
    # Protocolos
    if guidelines:
        print("\n📚 PROTOCOLOS MÉDICOS:")
        for idx, item in enumerate(guidelines[:3], 1):
            print(f"\n{idx}. {item['title']}")
            print(f"   {item['content'][:120]}...")
    else:
        print("\nℹ️  Nenhum protocolo específico encontrado para este caso")

    # IA
    if ai_response:
        print("\n" + "═"*50)
        print("🧠 EXPLICAÇÃO DO SISTEMA (Gemini 1.5 Flash)")
        print("═"*50)
        print(f"\n{ai_response}")

def main():
    try:
        # Inicialização
        display_banner()
        symptoms, history, age = get_user_input()
        
        # Componentes do sistema
        tree = MedicalDecisionTree()
        db = SingleStoreMed()
        ai = AIEnhancer()

        # Processamento
        print("\n⏳ Analisando sintomas com árvore de decisão...")
        diagnosis = tree.evaluate(symptoms, history, age)
        time.sleep(1)

        print("⏳ Consultando protocolos médicos...")
        guidelines = db.get_guidelines(diagnosis['categoria'])
        time.sleep(0.5)

        print("⏳ Gerando explicação com IA...")
        ai_response = ai.enhance_response(diagnosis, guidelines, symptoms)
        time.sleep(0.5)

        # Exibição
        display_results(diagnosis, guidelines, ai_response)

    except KeyboardInterrupt:
        print("\n❌ Operação cancelada pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"\n⚠️  Erro crítico: {str(e)}")
        print("Por favor, reinicie o sistema ou contate o suporte")
    finally:
        print("\n" + "═"*50)
        print("⚠️  Lembre-se: Este sistema não substitui avaliação médica presencial")
        print("© 2024 Sistema de Triagem Médica - Versão Terminal")

if __name__ == "__main__":
    main()