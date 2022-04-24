from tkinter import *


class ScrollableFrame(Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = Canvas(self, bg="green",scrollregion=(0,0,0,0))
        scrollbar = Scrollbar(self, orient=VERTICAL, command=canvas.yview)
        self.scrollable_frame = Frame(canvas)

        scrollbar.pack(side=LEFT, fill=Y)
        canvas.pack(side=RIGHT, fill="both", expand=True)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor=CENTER)

        canvas.configure(yscrollcommand=scrollbar.set)