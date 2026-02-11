# from fabric import Connection , task 


# c=Connection("ubuntu@44.201.180.250")


# def setup_mysql():
#     c.run("sudo apt update")
#     c.run("sudo apt install mysql-server -y")
#     c.run('mysql -u root -e "CREATE DATABASE class_activity;"')
#     c.put("backup.sql","/tmp/backup.sql")
#     c.run("mysql -u root class_activity < /tmp/backup.sql")


from fabric import Connection

c = Connection(host="44.201.180.250", user="ubuntu")


def setup_mysql():
    c.run("sudo apt update")
    c.run("sudo apt install mysql-server -y")
    c.run('sudo mysql -u root -e "CREATE DATABASE class_activity;"', warn=True)
    c.put("backup.sql", "/tmp/backup.sql")
    c.run("sed -i 's/PRAGMA.*;//g' /tmp/backup.sql")
    c.run("sed -i 's/BEGIN TRANSACTION;//g' /tmp/backup.sql")
    c.run("sed -i 's/COMMIT;//g' /tmp/backup.sql")
    c.run("sudo mysql -u root class_activity < /tmp/backup.sql")


if __name__ == "__main__":
    setup_mysql()