"""
数据库管理模块

功能：
1. SQLite数据库管理
2. 注射记录存储
3. 统计数据查询
4. 数据导出
"""

import sqlite3
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path

import pandas as pd


class DatabaseManager:
    """
    数据库管理器

    管理所有本地数据的存储和查询。
    """

    def __init__(self, db_path: str = "data/injection_monitoring.db"):
        """
        初始化数据库管理器

        Args:
            db_path: 数据库文件路径
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(
            str(self.db_path),
            check_same_thread=False,
            timeout=30
        )

        # 创建表
        self._create_tables()

    def _create_tables(self):
        """创建数据库表"""
        cursor = self.conn.cursor()

        # 用户表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER,
                weight_kg REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                profile TEXT
            )
        """)

        # 注射记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS injection_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                session_id TEXT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                site TEXT,
                angle REAL,
                duration REAL,
                success BOOLEAN,
                alerts TEXT,
                video_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # 告警历史表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alert_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_id INTEGER,
                alert_type TEXT,
                severity TEXT,
                message TEXT,
                timestamp TIMESTAMP,
                FOREIGN KEY (record_id) REFERENCES injection_records(id)
            )
        """)

        # 统计数据表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                date DATE,
                total_injections INTEGER DEFAULT 0,
                successful_count INTEGER DEFAULT 0,
                avg_angle REAL,
                avg_duration REAL,
                common_errors TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id, date)
            )
        """)

        self.conn.commit()
        print(f"[Database] 数据库初始化完成: {self.db_path}")

    def save_user(self, user_data: Dict[str, Any]) -> int:
        """
        保存用户信息

        Args:
            user_data: 用户数据
                {
                    "name": str,
                    "age": int,
                    "weight_kg": float,
                    "profile": dict
                }

        Returns:
            用户ID
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT INTO users (name, age, weight_kg, profile)
            VALUES (?, ?, ?, ?)
        """, (
            user_data["name"],
            user_data.get("age"),
            user_data.get("weight_kg"),
            json.dumps(user_data.get("profile", {}))
        ))

        self.conn.commit()
        return cursor.lastrowid

    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        获取用户信息

        Args:
            user_id: 用户ID

        Returns:
            用户数据字典
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT id, name, age, weight_kg, profile, created_at
            FROM users WHERE id = ?
        """, (user_id,))

        row = cursor.fetchone()

        if row:
            return {
                "id": row[0],
                "name": row[1],
                "age": row[2],
                "weight_kg": row[3],
                "profile": json.loads(row[4]) if row[4] else {},
                "created_at": row[5]
            }

        return None

    def save_injection_record(self, record: Dict[str, Any]) -> int:
        """
        保存注射记录

        Args:
            record: 注射记录
                {
                    "user_id": int,
                    "session_id": str,
                    "start_time": float,
                    "end_time": float,
                    "site": str,
                    "angle": float,
                    "duration": float,
                    "success": bool,
                    "alerts": list,
                    "video_path": str
                }

        Returns:
            记录ID
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT INTO injection_records
            (user_id, session_id, start_time, end_time, site, angle, duration, success, alerts, video_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record["user_id"],
            record["session_id"],
            record["start_time"],
            record["end_time"],
            record.get("site"),
            record.get("angle"),
            record.get("duration"),
            record.get("success", True),
            json.dumps(record.get("alerts", [])),
            record.get("video_path")
        ))

        self.conn.commit()
        record_id = cursor.lastrowid

        # 保存告警历史
        for alert in record.get("alerts", []):
            self._save_alert(record_id, alert)

        # 更新统计数据
        self._update_statistics(record["user_id"])

        return record_id

    def _save_alert(self, record_id: int, alert: Dict[str, Any]):
        """保存告警记录"""
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT INTO alert_history (record_id, alert_type, severity, message, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (
            record_id,
            alert.get("type"),
            alert.get("severity"),
            alert.get("message"),
            alert.get("timestamp", time.time())
        ))

        self.conn.commit()

    def get_injection_records(
        self,
        user_id: int,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        获取注射记录

        Args:
            user_id: 用户ID
            limit: 返回记录数量

        Returns:
            记录列表
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT id, user_id, session_id, start_time, end_time,
                   site, angle, duration, success, alerts, video_path
            FROM injection_records
            WHERE user_id = ?
            ORDER BY start_time DESC
            LIMIT ?
        """, (user_id, limit))

        rows = cursor.fetchall()

        records = []
        for row in rows:
            records.append({
                "id": row[0],
                "user_id": row[1],
                "session_id": row[2],
                "start_time": row[3],
                "end_time": row[4],
                "site": row[5],
                "angle": row[6],
                "duration": row[7],
                "success": row[8],
                "alerts": json.loads(row[9]) if row[9] else [],
                "video_path": row[10]
            })

        return records

    def get_user_statistics(
        self,
        user_id: int,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        获取用户统计数据

        Args:
            user_id: 用户ID
            days: 统计天数

        Returns:
            统计数据
        """
        cursor = self.conn.cursor()

        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        cursor.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful,
                AVG(angle) as avg_angle,
                AVG(duration) as avg_duration
            FROM injection_records
            WHERE user_id = ?
            AND date(start_time) >= ?
        """, (user_id, cutoff_date))

        row = cursor.fetchone()

        return {
            "total_injections": row[0] or 0,
            "successful_count": row[1] or 0,
            "success_rate": (row[1] / row[0] * 100) if row[0] > 0 else 0,
            "avg_angle": row[2] or 0,
            "avg_duration": row[3] or 0
        }

    def _update_statistics(self, user_id: int):
        """更新统计数据"""
        stats = self.get_user_statistics(user_id, days=30)

        cursor = self.conn.cursor()

        # 获取常见错误
        cursor.execute("""
            SELECT alert_type, severity, COUNT(*) as count
            FROM alert_history ah
            JOIN injection_records ir ON ah.record_id = ir.id
            WHERE ir.user_id = ?
            AND ah.timestamp >= datetime('now', '-30 days')
            GROUP BY alert_type, severity
            ORDER BY count DESC
            LIMIT 5
        """, (user_id,))

        common_errors = [dict(zip(["type", "severity", "count"], row)) for row in cursor.fetchall()]

        # 插入或更新统计
        cursor.execute("""
            INSERT OR REPLACE INTO statistics
            (user_id, date, total_injections, successful_count, avg_angle, avg_duration, common_errors, updated_at)
            VALUES (?, date('now'), ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            user_id,
            stats["total_injections"],
            stats["successful_count"],
            stats["avg_angle"],
            stats["avg_duration"],
            json.dumps(common_errors)
        ))

        self.conn.commit()

    def export_to_csv(
        self,
        user_id: int,
        output_path: str,
        days: int = 30
    ):
        """
        导出数据为CSV

        Args:
            user_id: 用户ID
            output_path: 输出文件路径
            days: 导出天数
        """
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        df = pd.read_sql_query("""
            SELECT * FROM injection_records
            WHERE user_id = ?
            AND date(start_time) >= ?
            ORDER BY start_time DESC
        """, self.conn, params=(user_id, cutoff_date))

        df.to_csv(output_path, index=False)
        print(f"[Database] 数据已导出到: {output_path}")

    def cleanup_old_data(self, days: int = 90):
        """
        清理旧数据

        Args:
            days: 保留天数
        """
        cursor = self.conn.cursor()

        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        # 删除旧记录
        cursor.execute("""
            DELETE FROM injection_records
            WHERE date(start_time) < ?
        """, (cutoff_date,))

        deleted_count = cursor.rowcount

        self.conn.commit()

        print(f"[Database] 已清理 {deleted_count} 条旧记录（超过 {days} 天）")

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            print("[Database] 数据库连接已关闭")
