import os
import json
import sqlite3
from datetime import datetime, timedelta
from .platform_utils import is_macos, get_default_font_family

APP_NAME = "DeskNoteX"
APP_VERSION = "1.0.0"

# Paths
APP_DIR = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), APP_NAME)
DB_PATH = os.path.join(APP_DIR, "data.db")
CONFIG_PATH = os.path.join(APP_DIR, "config.json")

# Default theme colors
THEME_LIGHT = {
    "window": "#FBF9F7",
    "card": "#FFFFFF",
    "text": "#333333",
    "text_secondary": "#666666",
    "border": "#E0E0E0",
    "accent": "#4A90D9",
    "hover": "#F0F0F0",
    "priority_high": "#FF6B6B",
    "priority_mid": "#FFB347",
    "priority_low": "#77DD77",
    "archive": "#F5F5F5",
    "input_bg": "#FFFFFF",
    "button_bg": "#4A90D9",
    "button_text": "#FFFFFF",
    "scrollbar": "#CCCCCC",
}

THEME_DARK = {
    "window": "#2C2C34",
    "card": "#383842",
    "text": "#E8E8EB",
    "text_secondary": "#A0A0A8",
    "border": "#4A4A55",
    "accent": "#5A9FE8",
    "hover": "#44444F",
    "priority_high": "#FF6B6B",
    "priority_mid": "#FFB347",
    "priority_low": "#77DD77",
    "archive": "#32323A",
    "input_bg": "#40404A",
    "button_bg": "#5A9FE8",
    "button_text": "#FFFFFF",
    "scrollbar": "#555560",
}

DEFAULT_CONFIG = {
    "theme": "light",
    "custom_colors": {},
    "font_family": "Microsoft YaHei",
    "font_size": 10,
    "window_pos": [100, 100],
    "window_size": [420, 640],
    "always_on_top": True,
    "auto_tuck": True,
    "tuck_edge": "right",
    "notifications_enabled": True,
    "category_colors": {
        "默认": "#4A90D9",
        "工作": "#FF6B6B",
        "学习": "#77DD77",
        "生活": "#FFB347",
    }
}

class ConfigManager:
    def __init__(self):
        os.makedirs(APP_DIR, exist_ok=True)
        self.config = self._load()
    
    def _load(self):
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Merge with defaults for any missing keys
                    merged = DEFAULT_CONFIG.copy()
                    merged.update(loaded)
                    return self._apply_platform_defaults(merged)
            except Exception:
                return self._apply_platform_defaults(DEFAULT_CONFIG.copy())
        return self._apply_platform_defaults(DEFAULT_CONFIG.copy())

    def _apply_platform_defaults(self, config):
        """根据平台覆盖默认中文字体。

        规则:仅当用户从未显式设置过 font_family(或等于原默认 "Microsoft YaHei")
        且当前为 macOS 时,替换为 PingFang SC。用户已自定义的值不动。
        """
        if is_macos() and config.get("font_family") in ("Microsoft YaHei", None, ""):
            config["font_family"] = get_default_font_family()
        return config
    
    def save(self):
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def get(self, key, default=None):
        return self.config.get(key, default)
    
    def set(self, key, value):
        self.config[key] = value
        self.save()
    
    def get_theme(self):
        theme_name = self.config.get("theme", "light")
        if theme_name == "dark":
            base = THEME_DARK.copy()
        else:
            base = THEME_LIGHT.copy()
        custom = self.config.get("custom_colors", {})
        base.update(custom)
        return base
    
    def get_font(self):
        return self.config.get("font_family", "Microsoft YaHei"), self.config.get("font_size", 10)

class DatabaseManager:
    def __init__(self):
        os.makedirs(APP_DIR, exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_tables()
    
    def _init_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                color TEXT DEFAULT '#4A90D9',
                sort_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                category_id INTEGER DEFAULT 1,
                priority INTEGER DEFAULT 1,
                status INTEGER DEFAULT 0,
                due_date TIMESTAMP,
                remind_time TIMESTAMP,
                remind_enabled INTEGER DEFAULT 1,
                repeat_type TEXT DEFAULT 'none',
                repeat_interval INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                archived INTEGER DEFAULT 0,
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reminders_sent (
                task_id INTEGER PRIMARY KEY,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Insert default category if not exists
        cursor.execute('''
            INSERT OR IGNORE INTO categories (id, name, color, sort_order) 
            VALUES (1, '默认', '#4A90D9', 0)
        ''')
        self.conn.commit()
    
    def add_category(self, name, color, sort_order=0):
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO categories (name, color, sort_order) VALUES (?, ?, ?)',
                (name, color, sort_order)
            )
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
    
    def get_categories(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM categories ORDER BY sort_order, id')
        return [dict(row) for row in cursor.fetchall()]
    
    def update_category(self, cat_id, name=None, color=None):
        cursor = self.conn.cursor()
        if name:
            cursor.execute('UPDATE categories SET name = ? WHERE id = ?', (name, cat_id))
        if color:
            cursor.execute('UPDATE categories SET color = ? WHERE id = ?', (color, cat_id))
        self.conn.commit()
    
    def delete_category(self, cat_id):
        cursor = self.conn.cursor()
        # Move tasks to default category
        cursor.execute('UPDATE tasks SET category_id = 1 WHERE category_id = ?', (cat_id,))
        cursor.execute('DELETE FROM categories WHERE id = ?', (cat_id,))
        self.conn.commit()
    
    def add_task(self, **kwargs):
        cursor = self.conn.cursor()
        fields = []
        values = []
        for k, v in kwargs.items():
            fields.append(k)
            values.append(v)
        placeholders = ','.join(['?' for _ in values])
        cursor.execute(f'INSERT INTO tasks ({",".join(fields)}) VALUES ({placeholders})', values)
        self.conn.commit()
        return cursor.lastrowid
    
    def get_tasks(self, category_id=None, status=None, archived=False, search=None):
        cursor = self.conn.cursor()
        query = 'SELECT t.*, c.name as category_name, c.color as category_color FROM tasks t LEFT JOIN categories c ON t.category_id = c.id WHERE t.archived = ?'
        params = [1 if archived else 0]
        if category_id is not None:
            query += ' AND t.category_id = ?'
            params.append(category_id)
        if status is not None:
            query += ' AND t.status = ?'
            params.append(status)
        if search:
            query += ' AND (t.title LIKE ? OR t.content LIKE ?)'
            params.extend([f'%{search}%', f'%{search}%'])
        query += ' ORDER BY t.priority DESC, t.due_date ASC, t.created_at DESC'
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def update_task(self, task_id, **kwargs):
        cursor = self.conn.cursor()
        for k, v in kwargs.items():
            cursor.execute(f'UPDATE tasks SET {k} = ? WHERE id = ?', (v, task_id))
        self.conn.commit()
    
    def delete_task(self, task_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        cursor.execute('DELETE FROM reminders_sent WHERE task_id = ?', (task_id,))
        self.conn.commit()
    
    def get_stats(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) as total FROM tasks WHERE archived = 0')
        total = cursor.fetchone()['total']
        cursor.execute('SELECT COUNT(*) as completed FROM tasks WHERE status = 1 AND archived = 0')
        completed = cursor.fetchone()['completed']
        cursor.execute('SELECT category_id, COUNT(*) as cnt FROM tasks WHERE archived = 0 GROUP BY category_id')
        by_cat = {row['category_id']: row['cnt'] for row in cursor.fetchall()}
        return {"total": total, "completed": completed, "completion_rate": round(completed / total * 100, 1) if total else 0, "by_category": by_cat}
    
    def get_pending_reminders(self):
        now = datetime.now()
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT t.*, c.name as category_name, c.color as category_color 
            FROM tasks t 
            LEFT JOIN categories c ON t.category_id = c.id 
            WHERE t.archived = 0 AND t.status = 0 AND t.remind_enabled = 1 
            AND t.remind_time IS NOT NULL AND t.remind_time <= ?
            AND t.id NOT IN (SELECT task_id FROM reminders_sent)
        ''', (now,))
        return [dict(row) for row in cursor.fetchall()]
    
    def mark_reminder_sent(self, task_id):
        cursor = self.conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO reminders_sent (task_id, sent_at) VALUES (?, ?)', 
                      (task_id, datetime.now()))
        self.conn.commit()
    
    def get_due_repeats(self):
        now = datetime.now()
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM tasks 
            WHERE archived = 0 AND status = 1 AND repeat_type != 'none'
            AND completed_at IS NOT NULL
        ''')
        tasks = [dict(row) for row in cursor.fetchall()]
        due_tasks = []
        for t in tasks:
            if not self._should_repeat(t, now):
                continue
            due_tasks.append(t)
        return due_tasks
    
    def _should_repeat(self, task, now):
        if not task['completed_at']:
            return False
        completed = datetime.fromisoformat(task['completed_at']) if isinstance(task['completed_at'], str) else task['completed_at']
        repeat = task['repeat_type']
        interval = task['repeat_interval'] or 1
        if repeat == 'daily':
            return (now - completed).days >= interval
        elif repeat == 'weekly':
            return (now - completed).days >= 7 * interval
        elif repeat == 'monthly':
            # Approximate month check
            return (now.year - completed.year) * 12 + now.month - completed.month >= interval
        elif repeat == 'yearly':
            return now.year - completed.year >= interval
        return False
    
    def spawn_repeat_task(self, task_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        row = cursor.fetchone()
        if not row:
            return
        task = dict(row)
        # Create new task with same properties but reset status
        now = datetime.now()
        new_due = None
        if task['due_date']:
            old_due = datetime.fromisoformat(task['due_date']) if isinstance(task['due_date'], str) else task['due_date']
            repeat = task['repeat_type']
            interval = task['repeat_interval'] or 1
            if repeat == 'daily':
                new_due = old_due + timedelta(days=interval)
            elif repeat == 'weekly':
                new_due = old_due + timedelta(weeks=interval)
            elif repeat == 'monthly':
                # Add months approximately
                month = old_due.month + interval
                year = old_due.year + (month - 1) // 12
                month = ((month - 1) % 12) + 1
                day = min(old_due.day, [31,29 if year%4==0 and (year%100!=0 or year%400==0) else 28,31,30,31,30,31,31,30,31,30,31][month-1])
                new_due = old_due.replace(year=year, month=month, day=day)
            elif repeat == 'yearly':
                new_due = old_due.replace(year=old_due.year + interval)
        
        cursor.execute('''
            INSERT INTO tasks (title, content, category_id, priority, status, due_date, remind_time, remind_enabled, repeat_type, repeat_interval, created_at)
            VALUES (?, ?, ?, ?, 0, ?, ?, ?, ?, ?, ?)
        ''', (task['title'], task['content'], task['category_id'], task['priority'], 
              new_due, task['remind_time'], task['remind_enabled'], task['repeat_type'], task['repeat_interval'], now))
        
        # Mark original as archived to avoid re-spawning
        cursor.execute('UPDATE tasks SET archived = 1 WHERE id = ?', (task_id,))
        self.conn.commit()
        return cursor.lastrowid
    
    def close(self):
        self.conn.close()
