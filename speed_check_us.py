#!/usr/bin/python3
import sys
import pexpect
from MAIN_DIAGA import DatabaseClient, DLinkTelnetClient
import cfg
import time

class InteractiveDLink(DLinkTelnetClient):
    def connect_interactive(self):
        """подключение без отключения clipaging"""
        try:
            print(f"Connect to {self.host}...")
            self.session = pexpect.spawn(f"telnet {self.host}", timeout=6)
            self.session.expect(r"User[Nn]ame:")
            self.session.sendline(self.username)
            self.session.expect(r"[Pp]ass[Ww]ord")
            self.session.sendline(self.password)
            self.session.expect(["5#", "admin#", "#", ">", "Switch#"], timeout=1)
            print("SUCCESSFUL")
            self.connected = True
            return True
        except Exception:
            print(f"Свитч упал: {self.host}")
            return False

def main():
    db = DatabaseClient(cfg.DB_CONFIG)
    if not db.connect():
        print("Ошибка подключения к БД")
        sys.exit(1)

    try:
        search = input("NOMBER CHILEN: ").strip()
        users = db.get_user_by_number(search)

        if not users:
            print("Абонент не найден")
            return

        for idx, user in enumerate(users, 1):
            print(f"INFO #{idx}: {user['switch']} | порт {user['port']}")

        if len(users) == 1:
            user = users[0]
            switch_ip = user["switch"]
            port = user["port"]

            switch = InteractiveDLink(switch_ip)
            if switch.connect_interactive():
                print("\nИнтерактивный режим. Введите 'exit' для выхода.\n")

                while True:
                    cmd = input(f"{switch_ip}> ").strip()
                    if cmd.lower() == 'exit':
                        break

                    switch.session.sendline(cmd)
                    time.sleep(1)
                    switch.session.sendline("")

                    try:
                        switch.session.expect(["5#", "admin#", "#", "Switch#"], timeout=2)
                        output = switch.session.before.decode(errors="ignore")
                        print(output)
                    except:
                        print("Timeout")

                switch.disconnect()

    except KeyboardInterrupt:
        print("\nВыход")
    finally:
        db.close()

if __name__ == "__main__":
    main()
