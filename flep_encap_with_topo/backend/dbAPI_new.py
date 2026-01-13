import pymysql


class DB:
    def __init__(self, port, user, password, db):
        self.conn = pymysql.connect(
            host="localhost", user=user, port=int(port), passwd=password, db=db
        )

        self.cur = self.conn.cursor(cursor=pymysql.cursors.DictCursor)

    def close(self):
        self.conn.close()

    def add(self, table, args):
        SQL = "insert into " + "`" + table + "`("
        key_list = args.keys()
        for key in key_list:
            SQL = SQL + "`" + key + "`" + ","
        SQL = SQL.strip(",")
        SQL = SQL + ")"
        SQL = SQL + " values ("
        for key in key_list:
            # MARK:修改为对args字符化
            SQL = SQL + '"' + str(args[key]) + '"' + ","
        SQL = SQL.strip(",")
        SQL = SQL + ")"
        print(SQL)
        try:
            self.cur.execute(SQL)
            self.conn.commit()
        except:
            self.conn.rollback()

    def delete(self, table, args):
        SQL = "delete from " + "`" + table + "` where "
        key_list = args.keys()
        for key in key_list:
            SQL = SQL + "`"+ key + "`" + ' = "' + str(args[key]) + '"' + " AND "
        SQL = SQL.strip("AND ")
        print(SQL)
        try:
            self.cur.execute(SQL)
            self.conn.commit()
        except:
            self.conn.rollback()

    def clear(self, table):
        SQL = "truncate table `" + table + "`"
        try:
            self.cur.execute(SQL)
            self.conn.commit()
        except:
            self.conn.rollback()

    def query(self, table, args):
        SQL = "select * from " + "`" + table + "` where "
        key_list = args.keys()
        if key_list:
            for key in key_list:
                SQL = SQL + key + ' = "' + str(args[key]) + '"' + " AND "
            SQL = SQL.strip("AND ")
        else:
            SQL = "select * from " + "`" + table + "`"
        # print(SQL)
        try:
            self.cur.execute(SQL)
            result = self.cur.fetchall()
            self.conn.commit()
            return result
        except:
            self.conn.rollback()


# id, target_ip, tp, port, rate, ceil, burst
if __name__ == "__main__":
    db = DB(port="3306", db="cloud", user="root", password="123456")
    # db.add_rule('15','10.0.0.1','tcp','11451','200','250','100')
    # db.add_rule('16','10.0.0.1','tcp','11451','200','250','100')
    # db.add_rule('17','10.0.0.2','udp','11451','200','250','100')

    # print(db.query_rule(ID='15'))
    # print(db.query_rule(IP='10.0.0.1'))
    # print(db.query_rule(TP='tcp'))

    # db.clear_rule()

    # db.delete_rule(IP='10.0.0.1')
    # db.delete_rule(ID='15', IP='10.0.0.1')
    # db.delete_rule(ID='15', IP='10.0.0.1', TP='tcp')
    # db.delete_rule(ID='15', IP='10.0.0.1', TP='tcp', TP_PORT='11451')
    # db.delete_rule(TP='udp')
    db.close()
