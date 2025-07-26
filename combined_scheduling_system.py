import mysql.connector
import math
from assignment_functions import *

# Database connection configuration
def get_database_connection():
    return mysql.connector.connect(
        user='root',
        password='',
        database='adzu',
        host='localhost'
    )

# ============================================================================
# SECTIONING MODULE (from SECTIONING.py)
# ============================================================================

def sectioning_module():
    """Create student sections based on enrollment data"""
    print("=== Starting Sectioning Module ===")
    
    conn = get_database_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM student_sections")
    conn.commit()
    cursor.execute("SELECT * FROM forecasted")
    initial = cursor.fetchall()
    sections = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z','AA','BB','CC','DD','EE','FF','GG','HH','II','JJ','KK','LL','MM','NN','OO','PP','QQ','RR']

    def get_number(program):
        cursor.execute(f"SELECT priority_number FROM department_data WHERE program = '{program}'")
        x = cursor.fetchall()
        priority_number = x[0][0]
        return priority_number

    for row in initial:
        program = row[0].replace(" ", "").upper()
        year = row[1]
        total_enrolled_count = row[2]
        if total_enrolled_count <= 40:
            section = 'A'
            print(program, total_enrolled_count, year, section)
            if total_enrolled_count <= 10:
                size = 'S'
            elif total_enrolled_count <= 20:
                size = 'M'
            else:
                size = 'L'
            priority_number = get_number(program)
            cursor.execute(f"INSERT INTO student_sections (program, year, section, size, priority_number) VALUES ('{program}', {year}, '{section}','{size}',{priority_number})")
            conn.commit()
        else:  
            print(f"total enrolled: {total_enrolled_count}")
            iterations = math.ceil(total_enrolled_count/35)
            print(iterations)
            for n in range(iterations):
                section = sections[n]
                priority_number = get_number(program)
                cursor.execute(f"INSERT INTO student_sections (program, year, section, size, priority_number) VALUES ('{program}', {year}, '{section}','L',{priority_number})")
                conn.commit()

    conn.close()
    print("=== Sectioning Module Completed ===")

# ============================================================================
# ROOM AND SCHEDULE GENERATION MODULE (from GENERATE ROOM AND SECTION SCHEDS.py)
# ============================================================================

def room_schedule_generation_module():
    """Generate room and section schedules"""
    print("=== Starting Room and Schedule Generation Module ===")
    
    conn = get_database_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM room_schedule")
    cursor.execute("DELETE FROM student_schedule")
    cursor.execute("DROP TABLE room_sched_remaining")      
    cursor.execute("DROP TABLE section_sched_remaining") 

    conn.commit()

    # Room schedule generation
    cursor.execute("SELECT room, size, type FROM rooms_data")
    room_data = cursor.fetchall()
    days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
    timeslots = ['8:00-9:20','9:30-10:50','11:00-12:20','12:30-1:50','2:00-3:20','3:30-4:30','4:30-5:50','6:00-7:20']
    
    for x in room_data:
        room = x[0]
        size = x[1]
        type = x[2]
        for day in days:
            if type != 'PE':
                for timeslot in timeslots:
                    cursor.execute(f"INSERT INTO room_schedule (room, size, type, day, timeslot) VALUES ('{room}','{size}','{type}','{day}','{timeslot}')")
                    conn.commit()
            else:
                timeslot1 = ['8:00-10:00','10:00-12:00','1:00-3:00','3:00-5:00']
                for timeslot in timeslot1:
                    cursor.execute(f"INSERT INTO room_schedule (room, size, type, day, timeslot) VALUES ('{room}','{size}','{type}','{day}','{timeslot}')")
                    conn.commit()

    # Section schedule generation
    cursor.execute("SELECT program, year, section FROM student_sections")
    section_data = cursor.fetchall()
    for y in section_data:
        program = y[0]
        year = y[1]
        section = y[2]
        program_year_section = f"{program}-{year}-{section}"
        for day in days:
            if day != 'Saturday':
                for timeslot in timeslots:
                    cursor.execute(f"INSERT INTO student_schedule (program_year_section, day, timeslot) VALUES ('{program_year_section}','{day}','{timeslot}')")
                    conn.commit() 
            else:
                timeslots1 = ['8:00-9:20','9:30-10:50','11:00-12:20','12:30-1:50','2:00-3:20']
                for timeslot in timeslots1:
                    cursor.execute(f"INSERT INTO student_schedule (program_year_section, day, timeslot) VALUES ('{program_year_section}','{day}','{timeslot}')")
                    conn.commit() 
 
    # Preparation for assignment
    cursor.execute("CREATE TABLE room_sched_remaining AS SELECT * FROM room_schedule")      
    cursor.execute("CREATE TABLE section_sched_remaining AS SELECT * FROM student_schedule") 
    conn.commit()

    conn.close()
    print("=== Room and Schedule Generation Module Completed ===")

# ============================================================================
# COURSE DISTRIBUTION MODULE (from COURSE DISTRIBUTION.py)
# ============================================================================

def course_distribution_module(sem=2):
    """Distribute courses to sections"""
    print("=== Starting Course Distribution Module ===")
    
    conn = get_database_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM initial")
    conn.commit()
    
    # Program dictionary
    programs = {
        'AEET':'aeet', 'BACOMM':'ba_comm', 'BAELS':'ba_els', 'BAINDIS':'ba_indis',
        'BAINTS':'ba_ints', 'BAPHILO':'ba_philo', 'BECED':'beced', 'BEED':'beed',
        'BPED':'bped', 'BSAC':'bsac_abm', 'BSACNON':'bsac_nonabm', 'BSBA':'bsba_entrep',
        'BSBAFM':'bsba_fm', 'BSBAMM':'bsba_mm', 'BSBIO':'bsbio', 'BSBIOBR':'bsbio_br',
        'BSBIOEB':'bsbio_eb', 'BSBME':'bsbme', 'BSCE':'bsce_cm', 'BSCEGEO':'bsce_geo',
        'BSCES':'bsce_s', 'BSCPE':'bscpe', 'BSCS':'bscs', 'BSECE':'bsece',
        'BSED':'bsed_english', 'BSEDFIL':'bsed_filipino', 'BSEDMATH':'bsed_math',
        'BSEDSCI':'bsed_science', 'BSED_SOCS':'bsed_socstud', 'BSEDVAL':'bsed_values',
        'BSIT':'bsit', 'BSLM':'bslm', 'BSMATH':'bsmath', 'BSMA':'bsma_abm',
        'BSMANON':'bsma_nonabm', 'BSN':'bsn', 'BSNMCA':'bsnmca', 'BSOA':'bsoa', 'BSPSY':'bspsyc'
    }

    # Course distribution
    cursor.execute("SELECT program, year, section, size FROM student_sections ORDER BY priority_number")
    p = cursor.fetchall()
    for x in p:
        program = x[0]
        year = x[1]
        section = x[2]
        size = x[3]
        cursor.execute(f"SELECT * FROM department_data WHERE program = '{program}'")
        d = cursor.fetchall()
        for a in d:
            department = a[1]
            priority_number = a[2]
        table_name = programs.get(program)
        if table_name:
            print(f"yes,{program}")
            cursor.execute(f"SELECT * FROM {table_name} WHERE sem = {sem} AND year = {year}")
            q = cursor.fetchall()
            for y in q:
                course_code = y[2]
                course_desc = y[3]
                units = y[4]
                type = y[5]
                print({program},{year},{department},{course_code})
                cursor.execute(f"INSERT INTO initial (course_code, course_section, program, section, year, department, size, type, course_desc) VALUES ('{course_code}','NONE','{program}','{section}',{year},'{department}','{size}','{type}','{course_desc}')")
                conn.commit()
        else:
            print(f"NO CURRICULUM FOR {program}")

    # Course sectioning
    sections = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z','AA','BB','CC','DD','EE','FF','GG','HH','II','JJ','KK','LL','MM','NN','OO','PP','QQ','RR']
    cursor.execute("SELECT course_code, COUNT(*) AS code_count FROM initial GROUP BY course_code")
    s = cursor.fetchall()
    for r in s:
        course_code = r[0]
        count = r[1]
        for n in range(count):
            print(n)
            course_section = sections[n]
            cursor.execute(f"SELECT program, section FROM initial WHERE course_code = '{course_code}' AND course_section = 'NONE' LIMIT 1")
            t = cursor.fetchall()
            print(t, course_section, course_code)
            for u in t:
                program = u[0]
                section = u[1]
                cursor.execute(f"UPDATE initial SET course_section = '{course_section}' WHERE program = '{program}' AND section ='{section}' AND course_code = '{course_code}'")
                conn.commit()

    # Course combination
    cursor.execute("SELECT * FROM initial WHERE size = 'S'")
    c = cursor.fetchall()
    for b in c:
        id1 = b[0]
        course_code = b[1]
        course_section = b[2]
        year1 = b[5]
        department = b[6]
        type = b[8]
        cursor.execute(f"SELECT * FROM initial WHERE id = {id1} AND partnered IS NULL")
        a = cursor.fetchall()
        if a:
            cursor.execute(f"SELECT * FROM initial WHERE course_code LIKE '%{course_code}%' AND department = '{department}' AND size = 'M'AND type = '{type}'LIMIT 1")
            e = cursor.fetchall()
            if e:
                for i in e:
                    course_section = i[2]
                    id2 = i[0]
                    year2 = i[5]
                    id_follow = min(id1,id2)
                    id_to_be_updated = max(id1,id2)
                    cursor.execute(f"SELECT course_section FROM initial where id = {id_follow}")
                    k = cursor.fetchall()
                    course_section_final = k[0][0]
                    print(course_section_final)
                    cursor.execute(f"UPDATE initial SET course_section = '{course_section_final}', size = 'L', partnered = 'YES' WHERE id = {id_to_be_updated}")
                    cursor.execute(f"UPDATE initial SET size = 'L', partnered = 'YES' WHERE id = {id_follow}")
                    conn.commit()            
            else:
                cursor.execute(f"SELECT * FROM initial WHERE course_code LIKE '%{course_code}%' AND department = '{department}' AND size = 'S' AND type = '{type}' AND id != {id1} LIMIT 1")
                f = cursor.fetchall()
                if f:
                    for i in f:
                        id2 = i[0]
                        program2 = i[3]
                        section2 = i[4]
                        year2 = i[5]
                        id_follow = min(id1,id2)
                        id_to_be_updated = max(id1,id2)
                        cursor.execute(f"SELECT course_section FROM initial where id = {id_follow}")
                        k = cursor.fetchall()
                        course_section_final = k[0][0]
                        print(course_section_final)
                        cursor.execute(f"UPDATE initial SET course_section = '{course_section_final}', size = 'L', partnered = 'YES' WHERE id = {id_to_be_updated}")
                        cursor.execute(f"UPDATE initial SET size = 'L', partnered = 'YES' WHERE id = {id_follow}")
                        conn.commit()  
                else:
                    continue            
        else:
            continue

    conn.close()
    print("=== Course Distribution Module Completed ===")

# ============================================================================
# LAB/LEC ASSIGNMENT MODULE (from LAB_LEC ASSIGNMENT.py)
# ============================================================================

def lab_lec_assignment_module():
    """Assign labs and lectures to rooms and timeslots"""
    print("=== Starting Lab/Lec Assignment Module ===")
    
    conn = get_database_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM initial WHERE program = 'BSN'")
    cursor.execute("DROP TABLE initial_backup")
    cursor.execute("CREATE TABLE IF NOT EXISTS initial_backup AS SELECT * FROM initial")
    cursor.execute("DELETE FROM assignment")
    conn.commit()

    program_year_section_assigned = {}
    room_day_timeslots = {}   
    programs_room = {
        'BSBIO': 'BIOLAB', 'BSPSY':'PSYCHOLOGYLAB', 'BACOMM':'MASSCOMLAB', 
        'BSECE':'ECELAB', 'BSCE':'CELAB', 'BSBME':'ECELAB', 'AEET':'ENGLAB'
    }

    # NSTP Assignment
    cursor.execute("SELECT DISTINCT course_code, course_section, size FROM initial WHERE course_code LIKE '%NSTP%'")   
    k = cursor.fetchall()
    for l in k:
        print(l)
        assigned = False
        course_code = l[0]
        course_section = l[1]
        size = l[2]
        timeslots, days = get_timeslots_days(type = 'NSTP')
        room = 'KIOSK'
        for day in days:
            if assigned:
                break
            for timeslot in timeslots:
                check1, check2 = lec2_checktimes(timeslot)
                nextday = day
                if assigned:
                    break
                student_available = student_avail_remove(cursor, course_code, course_section, day, nextday, check1, check2, program_year_section_assigned, conn)
                if student_available:
                    for_printing_assignment(cursor, conn, day, course_code, course_section, nextday, timeslot, room)
                    assigned = True
                    break
                else:
                    continue

    # PE Assignment
    cursor.execute("SELECT DISTINCT course_code, course_section FROM initial WHERE type = 'PE'")   
    k = cursor.fetchall()
    for l in k:
        print(l)
        print(room_day_timeslots)
        assigned = False
        course_code = l[0]
        course_section = l[1]
        timeslots, days = get_timeslots_days(type = 'PE')
        room_list = get_room(cursor, size = 'L' ,type = 'PE', dep_assigned = 'NONE')
        print(room_list)
        for room in room_list:
            if assigned:
                break
            for day in days:
                nextday = day
                if assigned:
                    break
                for timeslot in timeslots:
                    print(room, day, timeslot)
                    check1, check2 = pe_checktimes(timeslot)
                    room_combi_avail = check_dict(room_day_timeslots, room, day, nextday, check1 = timeslot, check2 = timeslot)
                    if assigned:
                        break
                    elif room_combi_avail:
                        student_available = student_avail_remove(cursor, course_code, course_section, day, nextday, check1, check2, program_year_section_assigned, conn)
                        if student_available:
                            removal_db("room_schedule", "room", room, cursor, conn, day, nextday, check1 = timeslot, check2 = timeslot)
                            appending(room_day_timeslots, room, day, nextday, check1 = timeslot, check2 = timeslot)
                            for_printing_assignment(cursor, conn, day, course_code, course_section, nextday, timeslot, room)
                            assigned = True
                            break
                        else:
                            continue    
                    else:
                        continue 

    # General subjects assignment
    gen_subs = ['MOD','PHIHIS','UNDSELF','SPIECO','ARTAPP','CONWOR','ETHICS','ELECTLM','ELECTGB','PURCOM','SCITECS','VOCMIS','RIZAL','FFP']
    for x in gen_subs:
        cursor.execute(f"SELECT DISTINCT course_code, course_section, size, department FROM initial WHERE course_code LIKE '%{x}%'") 
        print("here na") 
        k = cursor.fetchall()
        for l in k:
            print(l)
            assigned = False
            course_code = l[0]
            course_section = l[1]
            department = l[3]
            size = l[2]
            timeslots, days = get_timeslots_days(type = 'LEC')
            room_list = get_room(cursor, size ,type = 'LEC', dep_assigned = 'NONE')
            if not room_list:
                if size == 'S':
                    room_list = get_room(cursor, size = 'M' ,type = 'LEC', dep_assigned = 'NONE')
                else:
                    room_list = get_room(cursor, size = 'L' ,type = 'LEC', dep_assigned = 'NONE')
            print(room_list)
            for room in room_list:
                if assigned:
                    break
                for day in days:
                    if assigned:
                        break
                    for timeslot in timeslots:
                        if assigned:
                            break
                        check1 = timeslot
                        check2 = timeslot
                        nextday = get_nextday(day)
                        room_combi_avail = check_dict(room_day_timeslots, room, day, nextday, check1, check2)
                        print(room_combi_avail)
                        if room_combi_avail:
                            student_available = student_avail_remove(cursor, course_code, course_section, day, nextday, check1, check2, program_year_section_assigned, conn)
                            if student_available:
                                removal_db("room_schedule", "room", room, cursor, conn, day, nextday, check1, check2)
                                appending(room_day_timeslots, room, day, nextday, check1, check2)
                                for_printing_assignment(cursor, conn, day, course_code, course_section, nextday, timeslot, room)
                                assigned = True
                                break
                            else:
                                continue
                        else:
                            continue

    # OA courses assignment
    cursor.execute(f"SELECT DISTINCT course_code, course_section, size, department FROM initial WHERE course_code LIKE '%OA%'")
    print("here na") 
    k = cursor.fetchall()
    for l in k:
        print(l)
        assigned = False
        course_code = l[0]
        course_section = l[1]
        department = l[3]
        size = l[2]
        timeslots, days = get_timeslots_days(type = 'LEC')
        room_list = ['BC305']
        for room in room_list:
            if assigned:
                break
            for day in days:
                if assigned:
                    break
                for timeslot in timeslots:
                    if assigned:
                        break
                    check1 = timeslot
                    check2 = timeslot
                    nextday = get_nextday(day)
                    room_combi_avail = check_dict(room_day_timeslots, room, day, nextday, check1, check2)
                    print(room_combi_avail)
                    if room_combi_avail:
                        student_available = student_avail_remove(cursor, course_code, course_section, day, nextday, check1, check2, program_year_section_assigned, conn)
                        if student_available:
                            removal_db("room_schedule", "room", room, cursor, conn, day, nextday, check1, check2)
                            appending(room_day_timeslots, room, day, nextday, check1, check2)
                            for_printing_assignment(cursor, conn, day, course_code, course_section, nextday, timeslot, room)
                            assigned = True
                            break
                        else:
                            continue
                    else:
                        continue                   

    # Department-specific courses assignment
    add_in_query = """
        course_desc NOT LIKE '%programming%' 
        AND course_desc NOT LIKE '%computer%' 
        AND course_desc NOT LIKE '%computing%' 
        AND course_desc NOT LIKE '%Statistics%'
    """

    cursor.execute(f"SELECT DISTINCT course_code, course_section, size, department FROM initial WHERE size != 'L' AND {add_in_query}")
    print("here na") 
    k = cursor.fetchall()
    for l in k:
        print(l)
        assigned = False
        course_code = l[0]
        course_section = l[1]
        department = l[3]
        size = l[2]
        timeslots, days = get_timeslots_days(type = 'LEC')
        room_list = room_query(cursor, 'LEC', department, size)
        if not room_list:
            room_list = room_query(cursor, 'LEC', 'IGNORE', size)
        print(room_list)
        for room in room_list:
            if assigned:
                break
            for day in days:
                if assigned:
                    break
                for timeslot in timeslots:
                    if assigned:
                        break
                    check1 = timeslot
                    check2 = timeslot
                    nextday = get_nextday(day)
                    room_combi_avail = check_dict(room_day_timeslots, room, day, nextday, check1, check2)
                    print(room_combi_avail)
                    if room_combi_avail:
                        student_available = student_avail_remove(cursor, course_code, course_section, day, nextday, check1, check2, program_year_section_assigned, conn)
                        if student_available:
                            removal_db("room_schedule", "room", room, cursor, conn, day, nextday, check1, check2)
                            appending(room_day_timeslots, room, day, nextday, check1, check2)
                            for_printing_assignment(cursor, conn, day, course_code, course_section, nextday, timeslot, room)
                            assigned = True
                            break
                        else:
                            continue
                    else:
                        continue

    # CSITE programs assignment
    for x in programs_room:
        cursor.execute(f"""
        SELECT DISTINCT course_code, course_section, size, department, type 
        FROM initial 
        WHERE program = '{x}' 
        AND type != 'OJT' 
        AND {add_in_query}
        ORDER BY 
            CASE 
                WHEN type LIKE '%LAB%' THEN 1 
                WHEN type LIKE '%LEC%' THEN 2 
                ELSE 3 
            END
        """)
        print("here na")
        k = cursor.fetchall()
        for l in k:
            print(l)
            assigned = False
            course_code = l[0]
            course_section = l[1]
            department = l[3]
            size = l[2]
            type1 = l[4]
            print(department)
            rtype = programs_room.get(x)
            timeslots, days = get_timeslots_days(type1)
            room_list = room_query(cursor, rtype, 'IGNORE', size)
            if not room_list:
                room_list = room_query(cursor, rtype, 'IGNORE', 'IGNORE')
            for day in days:
                if assigned:
                    break
                for room in room_list:
                    if assigned:
                        break
                    for timeslot in timeslots:
                        check1, check2, nextday = get_timesdays(type1, timeslot, day)
                        if assigned:
                            break
                        print(nextday)
                        room_combi_avail = check_dict(room_day_timeslots, room, day, nextday, check1, check2)
                        print(room_combi_avail)
                        if room_combi_avail:
                            student_available = student_avail_remove(cursor, course_code, course_section, day, nextday, check1, check2, program_year_section_assigned, conn)
                            if student_available:
                                removal_db("room_schedule", "room", room, cursor, conn, day, nextday, check1, check2)
                                appending(room_day_timeslots, room, day, nextday, check1, check2)
                                for_printing_assignment(cursor, conn, day, course_code, course_section, nextday, timeslot, room)
                                assigned = True
                                break
                            else:
                                continue
                        else:
                            continue
            if not assigned:
                a = ws_consecutive(conn, cursor, course_code, course_section, room_list, program_year_section_assigned, room_day_timeslots)
                if a:
                    assigned = True
                else:
                    print("notmuch room")

    # Lectures assignment
    cursor.execute(f"SELECT DISTINCT course_code, course_section, size, department FROM initial WHERE type != 'OJT' AND {add_in_query}") 
    print("here na")  
    k = cursor.fetchall()
    for l in k:
        print(l)
        assigned = False
        course_code = l[0]
        course_section = l[1]
        department = l[3]
        size = l[2]
        timeslots, days = get_timeslots_days('LEC')
        type1 = 'LEC'
        room_list = room_query(cursor, 'IGNORE', department, size)
        if not room_list:
            room_list = room_query(cursor, 'LEC', department, size)
            if not room_list:
                room_list = room_query(cursor, 'IGNORE', department, 'L')
                
        for room in room_list:
            if assigned:
                break
            for day in days:
                if assigned:
                    break
                for timeslot in timeslots:
                    check1, check2, nextday = get_timesdays(type1, timeslot, day)
                    if assigned:
                        break
                    print(nextday)
                    room_combi_avail = check_dict(room_day_timeslots, room, day, nextday, check1, check2)
                    print(room_combi_avail)
                    if room_combi_avail:
                        student_available = student_avail_remove(cursor, course_code, course_section, day, nextday, check1, check2, program_year_section_assigned, conn)
                        if student_available:
                            removal_db("room_schedule", "room", room, cursor, conn, day, nextday, check1, check2)
                            appending(room_day_timeslots, room, day, nextday, check1, check2)
                            for_printing_assignment(cursor, conn, day, course_code, course_section, nextday, timeslot, room)
                            assigned = True
                            break
                        else:
                            continue
                    else:
                        continue
        if not assigned:
            a = ws_consecutive(conn, cursor, course_code, course_section, room_list, program_year_section_assigned, room_day_timeslots)
            if a:
                assigned = True
            else:
                room_list = room_query(cursor, 'LEC', 'NONE', size)
                for room in room_list:
                    if assigned:
                        break
                    for day in days:
                        if assigned:
                            break
                        for timeslot in timeslots:
                            check1, check2, nextday = get_timesdays(type1, timeslot, day)
                            if assigned:
                                break
                            print(nextday)
                            room_combi_avail = check_dict(room_day_timeslots, room, day, nextday, check1, check2)
                            print(room_combi_avail)
                            if room_combi_avail:
                                student_available = student_avail_remove(cursor, course_code, course_section, day, nextday, check1, check2, program_year_section_assigned, conn)
                                if student_available:
                                    removal_db("room_schedule", "room", room, cursor, conn, day, nextday, check1, check2)
                                    appending(room_day_timeslots, room, day, nextday, check1, check2)
                                    for_printing_assignment(cursor, conn, day, course_code, course_section, nextday, timeslot, room)
                                    assigned = True
                                    break
                                else:
                                    continue
                            else:
                                continue
                if not assigned:
                    a = ws_consecutive(conn, cursor, course_code, course_section, room_list, program_year_section_assigned, room_day_timeslots)
                    if a:
                        assigned = True
                    else:
                        b = late(conn, cursor, course_code, days, course_section, room_list, program_year_section_assigned, room_day_timeslots)
                        if b:
                            assigned = True
                        room_list = room_query(cursor, 'LEC', 'NONE', 'L')
                        for room in room_list:
                            if assigned:
                                break
                            for day in days:
                                if assigned:
                                    break
                                for timeslot in timeslots:
                                    check1, check2, nextday = get_timesdays(type1, timeslot, day)
                                    if assigned:
                                        break
                                    print(nextday)
                                    room_combi_avail = check_dict(room_day_timeslots, room, day, nextday, check1, check2)
                                    print(room_combi_avail)
                                    if room_combi_avail:
                                        student_available = student_avail_remove(cursor, course_code, course_section, day, nextday, check1, check2, program_year_section_assigned, conn)
                                        if student_available:
                                            removal_db("room_schedule", "room", room, cursor, conn, day, nextday, check1, check2)
                                            appending(room_day_timeslots, room, day, nextday, check1, check2)
                                            for_printing_assignment(cursor, conn, day, course_code, course_section, nextday, timeslot, room)
                                            assigned = True
                                            break
                                        else:
                                            continue
                                    else:
                                        continue
                        if not assigned:
                            a = ws_consecutive(conn, cursor, course_code, course_section, room_list, program_year_section_assigned, room_day_timeslots)
                            if a:
                                assigned = True
                            else:
                                b = late(conn, cursor, course_code, days, course_section, room_list, program_year_section_assigned, room_day_timeslots)
                                if b:
                                    assigned = True
                                print("notmuch room")

    conn.close()
    print("=== Lab/Lec Assignment Module Completed ===")

# ============================================================================
# MAIN EXECUTION FUNCTION
# ============================================================================

def main():
    """Main execution function that runs all modules in sequence"""
    print("=== SCHEDULING SYSTEM - COMBINED EXECUTION ===")
    print("Starting the complete scheduling process...")
    
    try:
        # Step 1: Sectioning
        sectioning_module()
        
        # Step 2: Room and Schedule Generation
        room_schedule_generation_module()
        
        # Step 3: Course Distribution
        course_distribution_module(sem=2)  # You can change the semester here
        
        # Step 4: Lab/Lec Assignment
        lab_lec_assignment_module()
        
        print("\n=== ALL MODULES COMPLETED SUCCESSFULLY ===")
        print("The scheduling system has finished processing all data.")
        
    except Exception as e:
        print(f"Error occurred during execution: {e}")
        print("Please check your database connection and data integrity.")

if __name__ == "__main__":
    main() 