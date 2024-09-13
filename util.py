import re

def clean_discord_message(input_string):
    bracket_pattern = re.compile(r'<[^>]+>')
    cleaned_content = bracket_pattern.sub('', input_string)
    return cleaned_content

async def split_and_send_messages(message_system, text, max_length):
    messages = [text[i:i + max_length] for i in range(0, len(text), max_length)]
    for string in messages:
        await message_system.channel.send(string)
