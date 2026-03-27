import socket
import threading
import tkinter as tk
import json
import uuid

HOST = "127.0.0.1"
PORT = 5050


class ClientGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Chat")
        self.master.geometry("500x600")
        self.master.configure(bg="#ECE5DD")

        # conexão
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((HOST, PORT))

        # ====== CONTAINER PRINCIPAL ======
        self.main_frame = tk.Frame(master, bg="#ECE5DD")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # ====== CANVAS (chat scrollável) ======
        self.canvas = tk.Canvas(self.main_frame, bg="#ECE5DD", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.main_frame, command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#ECE5DD")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # ====== INPUT ======
        self.bottom_frame = tk.Frame(master, bg="#ECE5DD")
        self.bottom_frame.pack(fill=tk.X)

        self.entry = tk.Entry(self.bottom_frame, font=("Arial", 12))
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=10)
        self.entry.bind("<Return>", lambda event: self.send_message())

        self.send_button = tk.Button(
            self.bottom_frame,
            text="SEND",
            bg="#25D366",
            fg="white",
            command=self.send_message
        )
        self.send_button.pack(side=tk.RIGHT, padx=10)

        threading.Thread(target=self.receive_messages, daemon=True).start()

    # ====== CRIAR BALÃO ======
    def add_message(self, text, sender="me"):
        frame = tk.Frame(self.scrollable_frame, bg="#ECE5DD")

        if sender == "me":
            bubble = tk.Label(
                frame,
                text=text,
                bg="#DCF8C6",
                wraplength=300,
                justify="left",
                padx=10,
                pady=5
            )
            bubble.pack(anchor="e", padx=10, pady=2)
        else:
            bubble = tk.Label(
                frame,
                text=text,
                bg="#FFFFFF",
                wraplength=300,
                justify="left",
                padx=10,
                pady=5
            )
            bubble.pack(anchor="w", padx=10, pady=2)

        frame.pack(fill=tk.BOTH)

        # auto scroll
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

    # ====== ENVIAR ======
    def send_message(self):
        message = self.entry.get()

        if message:
            msg_id = str(uuid.uuid4())

            payload = {
                "type": "message",
                "id": msg_id,
                "message": message
            }

            self.client_socket.sendall(json.dumps(payload).encode())

            # mostra no chat
            self.add_message(f"Você: {message}", "me")

            self.entry.delete(0, tk.END)

    # ====== RECEBER ======
    def receive_messages(self):
        while True:
            try:
                data = self.client_socket.recv(1024)
                if not data:
                    break

                response = json.loads(data.decode())

                if response["type"] == "ack":
                    self.add_message("✔ entregue", "me")

                elif response["type"] == "message":
                    self.add_message(
                        f"{response['from']}: {response['message']}",
                        "other"
                    )

            except:
                break


if __name__ == "__main__":
    root = tk.Tk()
    app = ClientGUI(root)
    root.mainloop()