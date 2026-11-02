"""Optional offline speech in a separate process so the camera never waits.

A new pyttsx3 engine is created for every word. Reusing one engine stays
silent after the first word on Windows.
"""
from multiprocessing import get_context
from queue import Empty, Full


def _speak_words(words, errors):
    import pyttsx3

    while True:
        word = words.get()
        if word is None:
            break
        engine = None
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", 170)
            engine.say(str(word))
            engine.runAndWait()
        except Exception as exc:
            try:
                errors.put_nowait(str(exc))
            except Exception:
                pass
        finally:
            if engine is not None:
                try:
                    engine.stop()
                except Exception:
                    pass


class SpeechOutput:
    def __init__(self):
        self.enabled = False
        self.error = None
        self._process = None
        self._words = None
        self._errors = None

    def ensure(self):
        if self.enabled:
            return
        ctx = get_context("spawn")
        self._words = ctx.Queue(maxsize=4)
        self._errors = ctx.Queue()
        self.error = None
        self._process = ctx.Process(target=_speak_words, args=(self._words, self._errors), daemon=True)
        try:
            self._process.start()
            self.enabled = True
        except Exception as exc:
            self.error = str(exc)
            self.close()

    def poll(self):
        if not self.enabled or self._errors is None:
            return
        try:
            self.error = self._errors.get_nowait()
        except Empty:
            if self._process is not None and self._process.is_alive():
                return
            self.error = "Speech process stopped unexpectedly"
        else:
            print(f"Speech error: {self.error}")
            return
        print(f"Speech unavailable: {self.error}")
        self.close()

    def say(self, word):
        if not self.enabled or self._words is None:
            return
        try:
            self._words.put_nowait(word)
        except Full:
            try:
                self._words.get_nowait()
            except Empty:
                pass
            try:
                self._words.put_nowait(word)
            except Full:
                pass

    def close(self):
        self.enabled = False
        if self._words is not None and self._process is not None and self._process.is_alive():
            try:
                self._words.put_nowait(None)
            except Exception:
                pass
        if self._process is not None and self._process.pid is not None:
            self._process.join(timeout=0.4)
            if self._process.is_alive():
                self._process.terminate()
                self._process.join(timeout=0.4)
        self._process = None
        for queue in (self._words, self._errors):
            if queue is not None:
                queue.cancel_join_thread()
                queue.close()
        self._words = self._errors = None
