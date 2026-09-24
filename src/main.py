import os
import threading

__version__ = "0.1.0"

os.environ["KIVY_GL_BACKEND"] = "sdl2"

from kivy.utils import platform

if platform != "android":
    from kivy.config import Config
    Config.set("input", "mouse", "mouse,multitouch_on_demand")

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.lang import Builder
from kivy.clock import Clock

from algoritmo import executar_algoritmo


Builder.load_file("app.kv")


class ResultadoPopup(BoxLayout):
    progresso = NumericProperty(0)
    progresso_texto = StringProperty("Preparando execução...")
    resultado = StringProperty("")
    executando = BooleanProperty(True)

    def fechar(self):
        if hasattr(self, "popup"):
            self.popup.dismiss()


class TelaPrincipal(BoxLayout):
    executando = BooleanProperty(False)

    def executar(self):
        if self.executando:
            return

        try:
            # Lê e valida os parâmetros
            nvar = int(self.ids.input_nvar.text)
            nos = int(self.ids.input_nos.text)
            max_geracoes = int(self.ids.input_geracoes.text)
            n_filhos = int(self.ids.input_filhos.text)

            mintermos = self.parse_mintermos(
                self.ids.input_mintermos.text
            )

            self.executando = True

            # Cria o conteúdo do modal
            self.modal_resultado = ResultadoPopup()

            # Cria o Popup
            self.popup_resultado = Popup(
                title="",
                content=self.modal_resultado,
                size_hint=(0.9, 0.85),
                auto_dismiss=False
            )

            # Permite que ResultadoPopup feche seu próprio Popup
            self.modal_resultado.popup = self.popup_resultado

            # Estado inicial
            self.modal_resultado.executando = True
            self.modal_resultado.progresso = 0
            self.modal_resultado.progresso_texto = "0%"
            self.modal_resultado.resultado = (
                "Executando algoritmo...\n"
                "Aguarde..."
            )

            # Abre o modal
            self.popup_resultado.open()

            # Executa o algoritmo fora da thread da interface
            thread = threading.Thread(
                target=self.executar_em_background,
                args=(
                    nvar,
                    nos,
                    max_geracoes,
                    n_filhos,
                    mintermos
                ),
                daemon=True
            )

            thread.start()

        except ValueError as e:
            self.exibir_erro(str(e))

    def parse_mintermos(self, texto):
        texto = texto.strip()

        if not texto:
            return []

        partes = texto.split(",")

        return [
            int(p.strip())
            for p in partes
            if p.strip() != ""
        ]

    def executar_em_background(
        self,
        nvar,
        nos,
        max_geracoes,
        n_filhos,
        mintermos
    ):
        try:
            res = executar_algoritmo(
                nvar=nvar,
                nos=nos,
                max_geracoes=max_geracoes,
                n_filhos=n_filhos,
                mintermos=mintermos,
                callback_progresso=self.receber_progresso
            )

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

            Clock.schedule_once(
                lambda dt: self.finalizar_execucao(texto)
            )

        except Exception as e:
            erro = str(e)

            Clock.schedule_once(
                lambda dt: self.finalizar_execucao(
                    f"Erro ao executar:\n{erro}",
                    erro=True
                )
            )

    def receber_progresso(
        self,
        geracao_atual,
        total_geracoes
    ):
        percentual = int(
            (geracao_atual / total_geracoes) * 100
        )

        Clock.schedule_once(
            lambda dt: self.atualizar_progresso(percentual)
        )

    def atualizar_progresso(self, percentual):
        if hasattr(self, "modal_resultado"):
            self.modal_resultado.progresso = percentual
            self.modal_resultado.progresso_texto = (
                f"{percentual}%"
            )

    def finalizar_execucao(self, texto, erro=False):
        if hasattr(self, "modal_resultado"):

            if erro:
                self.modal_resultado.progresso_texto = "Erro"
            else:
                self.modal_resultado.progresso = 100
                self.modal_resultado.progresso_texto = "100%"

            self.modal_resultado.resultado = texto
            self.modal_resultado.executando = False

        self.executando = False

    def exibir_erro(self, mensagem):
        conteudo = ResultadoPopup()

        popup = Popup(
            title="",
            content=conteudo,
            size_hint=(0.9, 0.6),
            auto_dismiss=False
        )

        conteudo.popup = popup
        conteudo.executando = False
        conteudo.progresso = 0
        conteudo.progresso_texto = "Erro nos parâmetros"
        conteudo.resultado = mensagem

        popup.open()


class MeuApp(App):
    def build(self):
        return TelaPrincipal()


if __name__ == "__main__":
    MeuApp().run()