from socket import gaierror
from django.db import models
from prefix_id import PrefixIDField
from rcon import Client, EmptyResponse, SessionTimeout, WrongPassword
from steam import game_servers as gs


class Server(models.Model):
    id = PrefixIDField(primary_key=True, prefix="server")
    ip = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    port = models.PositiveIntegerField()
    password = models.CharField(max_length=100, null=True, blank=True)
    rcon_password = models.CharField(max_length=100, null=True, blank=True)
    is_public = models.BooleanField(default=False)
    guild = models.ForeignKey(
        "guilds.Guild",
        on_delete=models.CASCADE,
        related_name="servers",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_connect_string(self):
        return f"connect {self.ip}:{self.port}; password {self.password};"

    def check_online(self):
        try:
            gs.a2s_info((self.ip, self.port))
            return True
        except (TimeoutError, ConnectionRefusedError, gaierror):
            return False

    def get_join_link(self):
        return f"steam://connect/{self.ip}:{self.port}/{self.password}"

    def send_rcon_command(self, command, *args):
        try:
            with Client(
                self.host,
                int(self.port),
                passwd=self.rcon_password,
            ) as client:
                return client.run(command, *args)
        except (EmptyResponse, SessionTimeout, WrongPassword) as e:
            print(f"Error sending RCON command: {e}")
            return None

    def __str__(self):
        return f"<{self.ip}:{self.port} - {self.name}>"
