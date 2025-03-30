#!/usr/bin/env python3
from decision_trees import MedicalDecisionTree
from singlestore_client import SingleStoreMed
from ai_enhancer import AIEnhancer
import os
import time
import logging
from dotenv import load_dotenv

# Configuração
load_dotenv()
logging.basicConfig(
    filename='medical_system.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

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
            if age >= 0:
                break
            print("⚠️  Idade não pode ser negativa")
        except ValueError:
            print("⚠️  Por favor, digite um número válido")

    return symptoms, history, age

def display_results(diagnosis, medical_info, ai_response):
    """Mostra os resultados formatados"""
    print("\n" + "═"*50)
    print("🔍 RESULTADOS DA TRIAGEM")
    print("═"*50)
    
    # Diagnóstico
    print(f"\n📌 Categoria: {diagnosis['category'].upper()}")
    print(f"🚨 Nível de Urgência: {diagnosis['urgency']}")
    
    if diagnosis['alerts']:
        print("\n⚠️  ALERTAS CLÍNICOS:")
        for alert in diagnosis['alerts']:
            print(f"    • {alert}")
    
    # Informações médicas
    if medical_info['relevant_info']:
        print("\n📚 INFORMAÇÕES RELEVANTES:")
        for idx, info in enumerate(medical_info['relevant_info'][:3], 1):
            print(f"\n{idx}. [Confiança: {info['confidence']}]")
            print(f"{info['text'][:200]}...")
    else:
        print("\nℹ️  Nenhuma informação específica encontrada")
    
    # Fontes
    if medical_info['sources']:
        print("\n📄 Fontes consultadas:")
        for source in medical_info['sources']:
            print(f"  - {os.path.basename(source)}")

    # IA
    if ai_response:
        print("\n" + "═"*50)
        print("🧠 EXPLICAÇÃO DO SISTEMA")
        print("═"*50)
        print(f"\n{ai_response}")

    # Recomendação
    print("\n" + "═"*50)
    print("⚠️  RECOMENDAÇÃO FINAL")
    print("═"*50)
    print(f"\n{medical_info['recommendation']}")

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
        time.sleep(1)  # Feedback visual

        print("⏳ Consultando protocolos médicos...")
        medical_info = db.get_medical_info(
            specialty_id=diagnosis['specialty_id'],
            user_query=symptoms
        )
        time.sleep(0.5)

        print("⏳ Gerando explicação com IA...")
        ai_response = ai.enhance_response(
            diagnosis=diagnosis,
            medical_info=medical_info,
            symptoms=symptoms
        )
        time.sleep(0.5)

        # Exibição
        display_results(diagnosis, medical_info, ai_response)

    except KeyboardInterrupt:
        print("\n❌ Operação cancelada pelo usuário")
    except Exception as e:
        logging.error(f"Erro crítico: {str(e)}", exc_info=True)
        print(f"\n⚠️  Erro no sistema: {str(e)}")
    finally:
        print("\n" + "═"*50)
        print("ℹ️  Lembre-se: Este sistema não substitui avaliação médica presencial")
        print("© 2024 Sistema de Triagem Médica - Versão Terminal")

if __name__ == "__main__":
    main()