package com.stgregorios.churchaccounting

import android.content.Context
import android.database.sqlite.SQLiteDatabase
import android.database.sqlite.SQLiteOpenHelper

class ChurchDatabaseHelper(context: Context) : SQLiteOpenHelper(context, DATABASE_NAME, null, DATABASE_VERSION) {

    companion object {
        const val DATABASE_NAME = "church_data_mobile.db"
        const val DATABASE_VERSION = 1
    }

    override fun onCreate(db: SQLiteDatabase) {
        db.execSQL("""
            CREATE TABLE IF NOT EXISTS cashbook (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                receipt_no TEXT,
                reg_no TEXT,
                name_of_hof TEXT,
                receipt_acct_head TEXT,
                receipt_code TEXT,
                receipt_details TEXT,
                receipt_cash REAL,
                receipt_bank REAL,
                payment_date TEXT,
                payment_voucher_no TEXT,
                payment_acct_head TEXT,
                payment_code TEXT,
                payment_details TEXT,
                payment_cash REAL,
                payment_bank REAL
            )
        """)
        
        db.execSQL("""
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reg_no TEXT,
                name TEXT,
                address TEXT,
                phone TEXT
            )
        """)

        db.execSQL("""
            CREATE TABLE IF NOT EXISTS account_heads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT,
                name TEXT,
                type TEXT
            )
        """)

        db.execSQL("""
            CREATE TABLE IF NOT EXISTS individual_ledgers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reg_no TEXT,
                particulars TEXT,
                amount REAL
            )
        """)
    }

    override fun onUpgrade(db: SQLiteDatabase, oldVersion: Int, newVersion: Int) {
        // Handle database upgrades if needed
        db.execSQL("DROP TABLE IF EXISTS cashbook")
        db.execSQL("DROP TABLE IF EXISTS members")
        db.execSQL("DROP TABLE IF EXISTS account_heads")
        db.execSQL("DROP TABLE IF EXISTS individual_ledgers")
        onCreate(db)
    }
}
