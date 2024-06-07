from customtkinter import CTkButton, CTkFont, CTkToplevel, CTkTextbox,CTkLabel

class CustomMessageBox(CTkToplevel):
    def __init__(self, parent, message):
        super().__init__(parent)
        self.geometry("500x350")
        self.title("Message")

        self.transient(parent)
        self.overrideredirect(True)  

        label = CTkLabel(self, text="Message", font=CTkFont(size=16, weight="bold"))
        label.pack(padx=20, pady=20)

        textbox = CTkTextbox(self, font=CTkFont(size=16, weight="bold"), width=460, height=190, wrap='word', state="disabled", border_spacing=30)
        textbox.pack(padx=20, pady=20)
        textbox.configure(state="normal")  # Temporarily make it editable to insert text
        textbox.insert("1.0", message)
        textbox.configure(state="disabled")  # Make it non-editable again

        button = CTkButton(self, text="OK", command=self.destroy)
        button.pack(pady=10)
        self.grab_set()

        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
        self.focus()


       
        
     