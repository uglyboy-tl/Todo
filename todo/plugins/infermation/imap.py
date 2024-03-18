import email
import imaplib
from dataclasses import dataclass

from loguru import logger

from todo.core import TodoItem
from todo.project import BaseContext, Option


@dataclass
class IMAP(BaseContext):
    imap_url: str
    username: str
    password: str
    imap_port: int = 993
    mailbox: str = "INBOX"

    def __call__(self, todo: TodoItem, process):
        # 连接到IMAP服务器
        mail = imaplib.IMAP4_SSL(self.imap_url, self.imap_port)
        mail.login(self.username, self.password)

        # 选择一个邮箱，例如INBOX
        status, messages = mail.select(self.mailbox)

        # 搜索邮件
        # 使用search方法搜索邮件，这里使用'ALL'作为搜索关键字获取所有邮件
        # 其他搜索关键字例如：'UNSEEN' 获取所有未读邮件，'SEEN' 获取所有已读邮件
        status, data = mail.search(None, "UNSEEN")

        # data是一个包含一个字符串的列表，该字符串包含邮件编号
        if status == "OK":
            mail_ids = data[0].split()
        else:
            logger.error("获取邮件失败")
            return

        num = len(mail_ids)
        if num == 1:
            latest_email_id = mail_ids[-1]  # 获取最后一封邮件的编号
            # 使用fetch方法获取邮件内容
            status, data = mail.fetch(latest_email_id, "(RFC822)")
            # 邮件原始内容
            raw_email = data[0][1]
            # 将原始内容解析为邮件消息
            email_message = email.message_from_bytes(raw_email)

            notify = TodoItem(f"{self.name} 收到来自 {email_message['From']} 的邮件 @notify @done")
            process(notify, Option.FORMAT | Option.ADD | Option.EXECUTE)
        elif num > 1:
            notify = TodoItem(f"{self.name} 收到 {num} 封邮件 @notify @done")
            process(notify, Option.FORMAT | Option.ADD | Option.EXECUTE)
