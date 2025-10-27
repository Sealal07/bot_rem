import aiosqlite

DB_NAME = 'reminders.db'

async def create_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            create table if not exists reminders(
                id integer primary key autoincrement,
                user_id integer,
                r_text text,
                r_date text,
                r_time text
            )
        ''')
        await db.execute('''
            create table if not exists user_timezones(
            user_id integer primary key,
            timezone text
            )
        ''')
        await  db.commit()

async def add_reminder(user_id, text, date, time):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            insert into reminders(user_id, r_text, r_date, r_time)
            values (?, ?, ?, ?)
        ''', (user_id, text, date, time))
        await db.commit()

async def get_user_reminder(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('''
            select id, r_text, r_date, r_time from reminders
            where user_id = ?
        ''', (user_id,))
        reminder = await cursor.fetchall()
        return reminder

async def delete_reminder(r_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            delete from reminders where id = ?
        ''', (r_id,))
        await db.commit()


async def set_user_timezone(user_id, timezone):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            insert into user_timezones(user_id, timezone)
            values (?, ?)
        ''', (user_id, timezone))

async def get_user_timezone(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('''
        select timezone from user_timezones
        where user_id = ?
        ''', (user_id,))
        result = await cursor.fetchone()
        return result[0] if result else None

async def get_all_reminders():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('''
            select id, user_id, r_text, r_date, r_time from reminders
        ''')
        reminders = await cursor.fetchall()
        return reminders