"""Optional offline speech in a separate process so the camera never waits."""
from multiprocessing import get_context
from queue import Empty, Full


def _speak_words(words, errors):
    try:
        import pyttsx3
        engine = pyttsx3.init()
        while True:
            word = words.get()
            engine.say(word)
            engine.runAndWait()
    except Exception as exc:
        errors.put(str(exc))


class SpeechOutput:
    def __init__(self):
        self.enabled = False
        self.error = None
        self._process = None
        self._words = None
        self._errors = None

    def toggle(self):
        if self.enabled:
            self.close()
        else:
            ctx = get_context("spawn")
            self._words = ctx.Queue(maxsize=3)
            self._errors = ctx.Queue()
            self.error = None
            self._process = ctx.Process(
                target=_speak_words, args=(self._words, self._errors), daemon=True
            )
            try:
                self._process.start()
                self.enabled = True
            except Exception as exc:
                self.error = str(exc)
                self.close()

    def poll(self):
        if not self.enabled:
            return
        try:
            self.error = self._errors.get_nowait()
        except Empty:
            if self._process.is_alive():
                return
            self.error = "Speech process stopped unexpectedly"
        print(f"Speech unavailable: {self.error}")
        self.close()

    def say(self, word):
        if self.enabled:
            try:
                self._words.put_nowait(word)
            except Full:
                pass  # Drop excess words instead of building a stale backlog.

    def close(self):
        self.enabled = False
        if self._process is not None and self._process.pid is not None:
            if self._process.is_alive():
                self._process.terminate()
            self._process.join()
        self._process = None
        for queue in (self._words, self._errors):
            if queue is not None:
                queue.cancel_join_thread()
                queue.close()
        self._words = self._errors = None
