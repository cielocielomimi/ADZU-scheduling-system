def get_timeslots_days (type):
    if type == 'PE':
        timeslots = ['8:00-10:00','10:00-12:00','1:00-3:00','3:00-5:00']
        days = ['Monday','Thursday','Tuesday','Friday','Wednesday','Saturday']
    elif type == 'NSTP':
        timeslots = ['8:00-10:50','12:30-3:20']
        days = ['Saturday']
    elif type == 'LEC2' or type == 'LAB2':
        timeslots = ['8:00-10:50','12:30-3:20']
        days = ['Wednesday','Monday','Tuesday']
    elif type == 'LEC':
        timeslots = ['8:00-9:20','9:30-10:50','11:00-12:20','12:30-1:50','2:00-3:20','4:30-5:50']
        days = ['Monday','Tuesday']
    elif type == 'LAB':
        timeslots = ['8:00-10:50','12:30-3:20']
        days = ['Wednesday','Saturday', 'Monday','Thursday','Tuesday','Friday']
    elif type == 'WS':
        timeslots = ['8:00-10:50','12:30-3:20']
        days = ['Wednesday','Saturday']
    return timeslots, days

def pe_checktimes(timeslot):
    if timeslot == '8:00-10:00':
        check1 = '8:00-9:20'
        check2 = '9:30-10:50'
    elif timeslot == '10:00-12:00':
        check1 = '9:30-10:50'
        check2 = '11:00-12:20'
    elif timeslot == '1:00-3:00':
        check1 = '12:30-1:50'
        check2 = '2:00-3:20'
    else:
        check1 = '2:00-3:20'
        check2 = '4:30-5:50'
    return check1, check2

def lec2_checktimes(timeslot):
    if timeslot == '8:00-10:50':
        check1 = '8:00-9:20'
        check2 = '9:30-10:50'
    elif timeslot == '12:30-3:20':
        check1 = '12:30-1:50'
        check2 = '2:00-3:20'
    elif timeslot == '4:30-7:20':
        check1 = '4:30-5:50'
        check2 = '6:00-7:20'
    return check1, check2
        
def get_nextday(day):
    if day == 'Monday':
        nextday = 'Thursday'
    elif day == 'Tuesday':
        nextday = 'Friday'
    elif day == 'Wednesday':
        nextday = 'Saturday'
    else:
        nextday = 'NONE'
    return nextday

def get_room(cursor, size,type, dep_assigned):
    room_list = []
    cursor.execute(f"SELECT room FROM rooms_data WHERE size = '{size}' AND type = '{type}' AND dep_assigned = '{dep_assigned}'")
    rooms = cursor.fetchall()
    for i in rooms:
        room_list.append(i[0])
    return room_list


def room_query(cursor, type, dep_assigned, size):
    query = "SELECT room FROM rooms_data WHERE"
    conditions = []
    if type != 'IGNORE':
        conditions.append(f"type = '{type}'")
    if dep_assigned != 'IGNORE':
        conditions.append(f"dep_assigned = '{dep_assigned}'")
    if size != 'IGNORE':
        conditions.append(f"size = '{size}'")

    if conditions:
        query += " " + " AND ".join(conditions)
    else:
        return []
    if query:
        cursor.execute(query)
        l = cursor.fetchall()
        room_list = [i[0] for i in l ] if l else []
    print(query)
    return room_list
                    

def get_timesdays(type, timeslot, day):
    if type =='WS' or type =='LAB':
        check1, check2 = lec2_checktimes(timeslot)
        nextday = day 
    elif type == 'LAB2' or type == 'LEC2':
        check1, check2 = lec2_checktimes(timeslot)
        nextday = get_nextday(day)
    else:
        check1 = timeslot
        check2 = timeslot
        nextday = get_nextday(day)  
    return check1, check2, nextday

#for nursing triples add     
def for_printing_assignment(cursor, conn, day, course_code, course_section, nextday, timeslot, room):
    day_codes = {'Monday':'M','Tuesday':'T','Wednesday':'W','Thursday':'Th','Friday':'F','Saturday':'S'}
    day_dual = {'Monday,Thursday':'MTh',
                'Tuesday,Friday':'TF',
                'Wednesday,Saturday':'WS'}
    course_code_section = f"{course_code}-{course_section}"
    a = check_sections(cursor, course_code, course_section)
    if a:
        program_year_section1, program_year_section2 = for_separation(cursor, course_code, course_section)
        program_year_section = f"{program_year_section1},{program_year_section2}"
    else:
        program_year_section = check_one(cursor, course_code, course_section)    
    if day == nextday:
        finalday = day_codes.get(day)
    else:
        day_tempo = f"{day},{nextday}"
        finalday = day_dual.get(day_tempo)
    cursor.execute(f"INSERT INTO assignment(course_code_section, program_year_section, room, day, timeslot) VALUES ('{course_code_section}','{program_year_section}','{room}','{finalday}','{timeslot}') ")
    cursor.execute(f"DELETE FROM initial WHERE course_code ='{course_code}' AND course_section ='{course_section}'")
    conn.commit() 
    return "done"
    
def student_avail_remove(cursor, course_code, course_section, day, nextday, check1, check2, program_year_section_assigned, conn):
    a = check_sections(cursor, course_code, course_section)
    if a:
        program_year_section1, program_year_section2 = for_separation(cursor, course_code, course_section)
        b = check_dict(program_year_section_assigned, program_year_section1, day, nextday, check1, check2)
        c = check_dict(program_year_section_assigned, program_year_section2, day, nextday, check1, check2)
        if b and c:
            d = check_consecutive(program_year_section_assigned, program_year_section1, day, nextday, check1)
            e = check_consecutive(program_year_section_assigned, program_year_section2, day, nextday, check1)
            if d and e:
                appending(program_year_section_assigned, program_year_section1, day, nextday, check1, check2)
                appending(program_year_section_assigned, program_year_section2, day, nextday, check1, check2)
                removal_db("student_schedule", "program_year_section", program_year_section1, cursor, conn, day, nextday, check1, check2)
                removal_db("student_schedule", "program_year_section", program_year_section2, cursor, conn, day, nextday, check1, check2)
                return True
            return False
        return False
    else:
        k = check_nonempty(cursor, course_code, course_section)
        if k:
            program_year_section1 = check_one(cursor, course_code, course_section)
            f = check_dict(program_year_section_assigned, program_year_section1, day, nextday, check1, check2)
            g = check_consecutive(program_year_section_assigned, program_year_section1, day, nextday, check1)
            if f and g:
                appending(program_year_section_assigned, program_year_section1, day, nextday, check1, check2)
                removal_db("student_schedule", "program_year_section", program_year_section1, cursor, conn, day, nextday, check1, check2)
                return True
            return False
        return False

def removal_db(table, comparison, keyword, cursor, conn, day, nextday, check1, check2):
    print(f"deleting here {check1},{check2},{day},{nextday}")
    cursor.execute(f"DELETE FROM {table} WHERE {comparison} = '{keyword}' AND day = '{day}' AND timeslot = '{check1}'")
    cursor.execute(f"DELETE FROM {table} WHERE {comparison} = '{keyword}' AND day = '{nextday}' AND timeslot = '{check1}'")
    cursor.execute(f"DELETE FROM {table} WHERE {comparison} = '{keyword}' AND day = '{day}' AND timeslot = '{check2}'")
    cursor.execute(f"DELETE FROM {table} WHERE {comparison} = '{keyword}' AND day = '{nextday}' AND timeslot = '{check2}'")
    conn.commit()
    
def check_consecutive(dict, to_be_checked, day, nextday, check1):
    timeslots = ['8:00-9:20','9:30-10:50','11:00-12:20','12:30-1:50','2:00-3:20','4:30-5:50']
    check1_index = get_time_index(check1)
    if check1_index is None or check1_index < 2:
        return True
    prev_time1 = timeslots[check1_index - 1]
    prev_time2 = timeslots[check1_index - 2]
    if day != nextday:
        assigned_slot1 = get_assigned_slots_for_day(dict, to_be_checked, day)
        assigned_slot2 = get_assigned_slots_for_day(dict, to_be_checked, nextday)
        if prev_time1 in assigned_slot1 and prev_time2 in assigned_slot1 or prev_time1 in assigned_slot2 and prev_time1 in assigned_slot2:
            return False
        return True
    elif day == nextday:
        assigned_slot1 = get_assigned_slots_for_day(dict, to_be_checked, day)
        if prev_time1 in assigned_slot1 and prev_time2 in assigned_slot1:
            return False
        return True
        
def check_sections(cursor, course_code, course_section):
    cursor.execute(f"SELECT program,year,section FROM initial WHERE course_code = '{course_code}' AND course_section = '{course_section}'")
    m = cursor.fetchall()
    if m and len(m)==2:
        return True
def check_nonempty(cursor, course_code, course_section):
    cursor.execute(f"SELECT program,year,section FROM initial WHERE course_code = '{course_code}' AND course_section = '{course_section}' LIMIT 1")
    m = cursor.fetchall()
    print(course_code, course_section, m)
    if m and len(m)==1:
        return True
    return False

def check_one(cursor, course_code, course_section):
    program1, year1, section1 = None, None, None
    cursor.execute(f"SELECT program,year,section FROM initial WHERE course_code = '{course_code}' AND course_section = '{course_section}' LIMIT 1")
    m = cursor.fetchall()
    print(course_code, course_section, m)
    if m and len(m)==1:
        program1, year1, section1 = m[0]
        program_year_section1 = f"{program1}-{year1}-{section1}" 
        return program_year_section1
    else:
        return None
    
def for_separation(cursor, course_code, course_section):
    program1, year1, section1 = None, None, None
    program2, year2, section2 = None, None, None
    cursor.execute(f"SELECT program,year,section FROM initial WHERE course_code = '{course_code}' AND course_section = '{course_section}'")
    m = cursor.fetchall()
    if m and len(m)==2:
        program1, year1, section1 = m[0]
        program2, year2, section2 = m[1] 
        program_year_section1 = f"{program1}-{year1}-{section1}"  
        program_year_section2 = f"{program2}-{year2}-{section2}"  
        return program_year_section1, program_year_section2
    print(m,len(m))
    return None, None
    
def check_dict(dict, to_be_checked, day, nextday, check1, check2):
    if to_be_checked not in dict:
        return True #available 
    if day != nextday and check1 == check2:
        if (day,check1) in dict[to_be_checked] or (nextday,check1) in dict[to_be_checked]:
            return False #not avail
        return True
    elif day != nextday and check1 != check2:
        if (day,check1) in dict[to_be_checked] or (nextday,check1) in dict[to_be_checked]:
            return False
        elif (day,check2) in dict[to_be_checked] or (nextday,check2) in dict[to_be_checked]:
            return False
        else:
            return True
    elif day == nextday and check1 != check2:
        if (day,check1) in dict[to_be_checked] or (day,check2) in dict[to_be_checked]:
            return False #not avail
        return True
    elif day == nextday and check1 == check2:
        if (day,check1) in dict[to_be_checked]:
            return False
        return True
        

#twice call for 2 programs
def appending(dict, to_be_appended, day, nextday, check1, check2):
    if to_be_appended not in dict:
        dict[to_be_appended] = []
    if day != nextday and check1 == check2:
        dict[to_be_appended].append((day, check1))
        dict[to_be_appended].append((nextday, check1))
    elif day != nextday and check1 != check2:
        dict[to_be_appended].append((day, check1))
        dict[to_be_appended].append((nextday, check1))
        dict[to_be_appended].append((day, check2))
        dict[to_be_appended].append((nextday, check2))
    elif day == nextday and check1 != check2:
        dict[to_be_appended].append((day, check1))
        dict[to_be_appended].append((day, check2))
    elif day == nextday and check1 == check2:
        dict[to_be_appended].append((day, check1))
    return "done"


def ws_consecutive(conn, cursor, course_code, course_section, room_list, program_year_section_assigned, room_day_timeslots):
    timeslots, days = get_timeslots_days (type = 'WS')
    assigned = False
    for day in days:
        if assigned:
            break
        for timeslot in timeslots:
            if assigned:
                break
            check1, check2 = lec2_checktimes(timeslot)
            nextday = day
            for room in room_list:
                room_combi_avail = check_dict(room_day_timeslots, room, day, nextday, check1, check2)
                if room_combi_avail:
                    student_available = student_avail_remove(cursor, course_code, course_section, day, nextday, check1, check2, program_year_section_assigned, conn)
                    if student_available:
                        removal_db("room_schedule", "room", room, cursor, conn, day, nextday, check1, check2)
                        appending(room_day_timeslots, room, day, nextday, check1, check2)
                        for_printing_assignment(cursor, conn, day, course_code, course_section, nextday, timeslot, room)
                        return True
                    else:
                        continue
                else:
                    continue   
    if not assigned:
        day = 'Wednesday'
        nextday = 'Saturday'
        timeslot = '11:00-12:20'
        check1 = timeslot
        check2 = timeslot
        for room in room_list:
            room_combi_avail = check_dict(room_day_timeslots, room, day, nextday, check1, check2)
            if room_combi_avail:
                student_available = student_avail_remove(cursor, course_code, course_section, day, nextday, check1, check2, program_year_section_assigned, conn)
                if student_available:
                    removal_db("room_schedule", "room", room, cursor, conn, day, nextday, check1, check2)
                    appending(room_day_timeslots, room, day, nextday, check1, check2)
                    for_printing_assignment(cursor, conn, day, course_code, course_section, nextday, timeslot, room)
                    return True
                else:
                    continue
            else:
                continue 
        if not assigned:
            day = 'Wednesday'
            nextday = day
            timeslot = '4:30-7:20'
            check1, check2 =lec2_checktimes(timeslot)
            for room in room_list:
                room_combi_avail = check_dict(room_day_timeslots, room, day, nextday, check1, check2)
                if room_combi_avail:
                    student_available = student_avail_remove(cursor, course_code, course_section, day, nextday, check1, check2, program_year_section_assigned, conn)
                    if student_available:
                        removal_db("room_schedule", "room", room, cursor, conn, day, nextday, check1, check2)
                        appending(room_day_timeslots, room, day, nextday, check1, check2)
                        for_printing_assignment(cursor, conn, day, course_code, course_section, nextday, timeslot, room)
                        return True
                    else:
                        continue
                else:
                    continue 
            if not assigned:
                return False

def get_time_index(check1):
    timeslots = ['8:00-9:20','9:30-10:50','11:00-12:20','12:30-1:50','2:00-3:20','4:30-5:50']
    return timeslots.index(check1) if check1 in timeslots else None

def get_assigned_slots_for_day(program_year_section_assigned, program_year_section, day):
    if program_year_section not in program_year_section_assigned:
        return [] 
    return [slot[1] for slot in program_year_section_assigned[program_year_section] if slot[0] == day]

def room_particular(comparison, key,cursor):
    cursor.execute(f"SELECT room FROM rooms_data WHERE {comparison}='{key}'")
    b = cursor.fetchall()
    room_list = [i[0] for i in b]
    return room_list
    
     
def late(conn, cursor, course_code, days, course_section, room_list, program_year_section_assigned, room_day_timeslots):
    timeslot = '6:00-7:20'
    assigned = False
    for day in days:
        if assigned:
            break
        check1 = timeslot
        check2 = timeslot
        nextday = get_nextday(day)
        for room in room_list:
            room_combi_avail = check_dict(room_day_timeslots, room, day, nextday, check1, check2)
            if room_combi_avail:
                student_available = student_avail_remove(cursor, course_code, course_section, day, nextday, check1, check2, program_year_section_assigned, conn)
                if student_available:
                    removal_db("room_schedule", "room", room, cursor, conn, day, nextday, check1, check2)
                    appending(room_day_timeslots, room, day, nextday, check1, check2)
                    for_printing_assignment(cursor, conn, day, course_code, course_section, nextday, timeslot, room)
                    return True
                else:
                    continue
            else:
                continue   
    if not assigned:
        return False       
            


   

#di to nagamit eto dapat sa lec part pero pagod na ako magisip sa next na                 
def adjust_roomsize(size, days, timeslots, room_day_timeslots, program_year_section_assigned, cursor, conn, course_section, course_code):
    assigned = False
    if size == 'S':
        adjusted_size = 'M'
    else:
        adjusted_size = 'L'
    room_list = get_room(cursor, adjusted_size ,type = 'LEC', dep_assigned = 'NONE')
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
                if assigned:
                    break
                elif room_combi_avail:#here na
                    student_available = student_avail_remove(cursor, course_code, course_section, day, nextday, check1, check2, program_year_section_assigned, conn)
                    if student_available:
                        removal_db("room_schedule", "room", room, cursor, conn, day, nextday, check1, check2)
                        appending(room_day_timeslots, room, day, nextday, check1, check2)
                        for_printing_assignment(cursor, conn, day, course_code, course_section, nextday, timeslot, room)
                        assigned = True
                        return True
                    else:
                        continue
                else:
                    continue
    if not assigned:
        a = ws_consecutive(conn, cursor, course_code, course_section, room_list, program_year_section_assigned, room_day_timeslots)
        if a:
            assigned = True  
            return True 
        else:
            room_list = get_room(cursor, 'L' ,type = 'LEC', dep_assigned = 'NONE')
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
                        if assigned:
                            break
                        elif room_combi_avail:#here na
                            student_available = student_avail_remove(cursor, course_code, course_section, day, nextday, check1, check2, program_year_section_assigned, conn)
                            if student_available:
                                removal_db("room_schedule", "room", room, cursor, conn, day, nextday, check1, check2)
                                appending(room_day_timeslots, room, day, nextday, check1, check2)
                                for_printing_assignment(cursor, conn, day, course_code, course_section, nextday, timeslot, room)
                                assigned = True
                                return True
                            else:
                                continue
                        else:
                            continue
            if not assigned:
                return False