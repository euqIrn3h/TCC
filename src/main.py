import os
import time
import threading

inicio = time.time()
print("1. Início do arquivo")

os.environ["KIVY_GL_BACKEND"] = "sdl2"

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.lang import Builder
from kivy.clock import Clock
from algoritmo import executar_algoritmo

Builder.load_file("app.kv")



class TelaPrincipal(BoxLayout):
    resultado = StringProperty(
        "Clique em 'Executar algoritmo' para gerar um circuito lógico."
    )
    progresso = NumericProperty(0)
    progresso_texto = StringProperty("0%")
    executando = BooleanProperty(False)

    def executar(self):
        if self.executando:
            return

        self.executando = True
        self.progresso = 0
        self.progresso_texto = "0%"
        self.resultado = "Executando algoritmo...\nAguarde..."

        thread = threading.Thread(target=self.executar_em_background, daemon=True)
        thread.start()

    def executar_em_background(self):
        try:
            res = executar_algoritmo(callback_progresso=self.receber_progresso)

            texto = (
                f"{res['mensagem']}\n"
                f"{'-' * 40}\n"
                f"Fitness: {res['fitness']}\n"
                f"Gerações: {res['geracoes']}\n"
                f"Nós ativos: {res['nos_ativos']}\n\n"
                f"Expressão booleana:\n"
                f"{res['expressao']}\n\n"
                f"Indivíduo:\n"
                f"{res['individuo']}"
            )

            Clock.schedule_once(lambda dt: self.finalizar_execucao(texto))

        except Exception as e:
            Clock.schedule_once(
                lambda dt: self.finalizar_execucao(f"Erro ao executar:\n{str(e)}")
            )

    def receber_progresso(self, geracao_atual, total_geracoes):
        percentual = int((geracao_atual / total_geracoes) * 100)
        Clock.schedule_once(
            lambda dt: self.atualizar_progresso(percentual)
        )

    def atualizar_progresso(self, percentual):
        self.progresso = percentual
        self.progresso_texto = f"{percentual}%"

    def finalizar_execucao(self, texto):
        self.progresso = 100
        self.progresso_texto = "100%"
        self.resultado = texto
        self.executando = False

class MeuApp(App):
    def build(self):
        return TelaPrincipal()


if __name__ == "__main__":
    MeuApp().run()
    print("11. Depois do run:", time.time() - inicio)