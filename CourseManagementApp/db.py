import oracledb
from .user import Member, AdminUser, ServerAdmin
from .course import Course
from .term import Term
from .domain import Domain
from .competency import Competency
from .element import Element
from .exceptions import ObjectAlreadyExists, CannotFindObject
import os
class Database:
    def __init__(self, autocommit=True):
        self.__connection = self.__connect()
        self.__connection.autocommit = autocommit

    def run_file(self, file_path):
        statement_parts = []
        with self.__connection.cursor() as cursor:
            with open(file_path, 'r') as f:
                for line in f:
                    statement_parts.append(line)
                    if line.strip('\n').strip('\n\r').strip().endswith(';'):
                        statement = "".join(
                            statement_parts).strip().rstrip(';')
                        if statement:
                            try:
                                cursor.execute(statement)
                            except Exception as e:
                                print(e)
                        statement_parts = []
    
    # User Functions
    def add_user(self, user):
        try:
            access_group = 1
            if isinstance(user, AdminUser):
                access_group = 2
            elif isinstance(user, ServerAdmin):
                access_group = 3
            blocked = 0
            if user.blocked:
                blocked = 1
            with self.__get_cursor() as cursor:
                cursor.execute("INSERT INTO course_users(name,password,email,access_group,date_created, blocked) VALUES(:name, :password, :email, :access_group, :date_created, :blocked)", 
                               name=user.name, password=user.password, email=user.email, access_group=access_group, date_created=user.date_created, blocked=blocked)
        except oracledb.IntegrityError:
            raise ObjectAlreadyExists('Email already taken')
        
    def edit_user(self, name, email):
        try:
            with self.__get_cursor() as cursor:
                cursor.execute("update course_users set name=:name where email=:email", name=name, email=email)
        except oracledb.IntegrityError:
            raise CannotFindObject('Object does not exist')

    def update_user_pwd(self, email, new_pwd):
        try:
            with self.__get_cursor() as cursor:
                cursor.execute("update course_users set password=:new_password where email=:email",
                               new_password=new_pwd,email=email)
        except oracledb.IntegrityError:
            raise CannotFindObject('Object does not exist')
        
    def get_users(self):
        users = []
        with self.__get_cursor() as cursor:
            results = cursor.execute('SELECT name,password,email,access_group,user_id, date_created, blocked FROM course_users order by user_id')
            for row in results:
                user = self.convert_user_group(row)
                users.append(user)
        return users

    def convert_user_group(self,row):
        if row[3] == 1:
            user = Member(row[0], row[1], row[2], row[5], row[6])
        elif row[3] == 2:
            user = AdminUser(row[0], row[1], row[2], row[5], row[6])
        else:
            user = ServerAdmin(row[0], row[1], row[2], row[5], row[6])
        user.id = row[4]
        return user
    
    def get_members(self):
        users = []
        with self.__get_cursor() as cursor:
            results = cursor.execute('SELECT name,password,email,access_group,user_id, date_created, blocked FROM course_users where access_group = 1 order by user_id')
            for row in results:
                user = self.convert_user_group(row)
                users.append(user)
        return users
    
    def get_user_by_email(self, email):
        try:
            with self.__get_cursor() as cursor:
                results = cursor.execute('SELECT name, password, email, access_group, user_id, date_created, blocked FROM course_users WHERE email=:email', email=email)
                for row in results:
                    user = self.convert_user_group(row)
                    return user
        except oracledb.IntegrityError as e:
            return None
        
    def block_user_db(self,email):
        user = self.get_user_by_email(email)
        if user.blocked == 1:
            block = 0
        else:
            block = 1
        try:
            with self.__get_cursor() as cursor:
                cursor.execute('UPDATE course_users SET blocked=:block_status WHERE email=:email', block_status=block, email=email)
        except oracledb.IntegrityError as e:
            return CannotFindObject("User does not exist")

        
    def get_user_by_id(self, user_id):
        try:
            with self.__get_cursor() as cursor:
                results = cursor.execute('SELECT name, password, email, access_group, user_id, date_created, blocked FROM course_users WHERE user_id=:user_id', user_id=user_id)
                for row in results:
                    user = self.convert_user_group(row)
                    return user
        except oracledb.IntegrityError as e:
            return None
        
    def edit_user_group(self, new_group, email):
        if new_group == 'Server Admin':
            new_group = 3
        elif new_group == 'Admin':
            new_group = 2
        else:
            new_group = 1
        try:
            with self.__get_cursor() as cursor:
                cursor.execute('UPDATE course_users SET access_group=:access_group WHERE email=:email', access_group=new_group, email=email)
        except oracledb.IntegrityError as e:
            raise CannotFindObject('User does not exist')
        
    def del_user(self, email):
        try:
            with self.__get_cursor() as cursor:
                cursor.execute('DELETE FROM course_users WHERE email=:email', email=email)
        except oracledb.IntegrityError as e:
            raise CannotFindObject('User does not exist')
    
    # Term Functions
    def add_term(self, term):
        try:
            with self.__get_cursor() as cursor:
                cursor.execute("INSERT INTO terms (term_id, term_name) VALUES(:term_id, :term_name)", 
                               term_id=term.term_id, term_name=term.term_name)
        except oracledb.IntegrityError as e:
            raise ObjectAlreadyExists('Term already exists')
    
    def get_term(self, term_id):
        try:
            with self.__get_cursor() as cursor:
                results = cursor.execute('SELECT term_id, term_name FROM terms WHERE term_id=:term_id', term_id=term_id)
                for row in results:
                    term = Term(row[0])
                    if 'Fall' not in row[1] and 'Winter' not in row[1]:
                        term.term_name = row[1]
                    return term
        except oracledb.IntegrityError as e:
            return None
    
    def get_terms(self):
        terms = []
        with self.__get_cursor() as cursor:
            results = cursor.execute('SELECT term_id, term_name FROM terms ORDER BY term_id')
            for row in results:
                term = Term(row[0])
                if 'Fall' not in row[1] and 'Winter' not in row[1]:
                    term.term_name = row[1]
                terms.append(term)
        return terms
    
    def get_terms_for_api(self, page_size, page_number):
        terms = []
        previous_page = None
        next_page = None
        offset = (page_number - 1) * page_size
        with self.__get_cursor() as cursor:
            results = cursor.execute('SELECT term_id, term_name FROM terms ORDER BY term_id OFFSET :offset ROWS FETCH NEXT :page_size ROWS ONLY', 
                                        offset=offset, page_size=page_size)
            for row in results:
                term = Term(row[0])
                if 'Fall' not in row[1] and 'Winter' not in row[1]:
                    term.term_name = row[1]
                terms.append(term)
        if page_number > 1:
            previous_page = page_number - 1
        if len(terms) > 0 and (len(terms) >= page_size):
            next_page = page_number + 1
        return terms, previous_page, next_page
        
    def edit_term(self, term_id, new_term):
        try:
            with self.__get_cursor() as cursor:
                cursor.execute('UPDATE terms SET term_name=:term_name WHERE term_id=:term_id', term_name=new_term.term_name, term_id=term_id)
        except oracledb.IntegrityError as e:
            raise CannotFindObject('Term does not exist')
        
    def del_term(self, term_id):
        try:
            with self.__get_cursor() as cursor:
                cursor.execute('DELETE FROM terms WHERE term_id=:term_id', term_id=term_id)
        except oracledb.IntegrityError as e:
            raise CannotFindObject('Term does not exist')
    
    # Domain Functions
    def add_domain(self, domain):
        try:
            with self.__get_cursor() as cursor:
                cursor.execute("INSERT INTO domains (domain, domain_description) VALUES(:domain, :domain_description)", 
                               domain=domain.domain, domain_description=domain.domain_description)
        except oracledb.IntegrityError as e:
            raise ObjectAlreadyExists('Domain already exists')
    
    def get_domain(self, domain_id):
        try:
            with self.__get_cursor() as cursor:
                results = cursor.execute('SELECT domain_id, domain, domain_description FROM domains WHERE domain_id=:domain_id', domain_id=domain_id)
                for row in results:
                    domain = Domain(row[1], row[2])
                    domain.domain_id = row[0]
                    return domain
        except oracledb.IntegrityError as e:
            return None
    
    def get_domains(self):
        domains = []
        with self.__get_cursor() as cursor:
            results = cursor.execute('SELECT domain_id, domain, domain_description FROM domains ORDER BY domain_id')
            for row in results:
                domain = Domain(row[1], row[2])
                domain.domain_id = row[0]
                domains.append(domain)
        return domains
    
    def get_domains_for_api(self, page_size, page_number):
        domains = []
        previous_page = None
        next_page = None
        offset = (page_number - 1) * page_size
        with self.__get_cursor() as cursor:
            results = cursor.execute('SELECT domain_id, domain, domain_description FROM domains ORDER BY domain_id OFFSET :offset ROWS FETCH NEXT :page_size ROWS ONLY', 
                                        offset=offset, page_size=page_size)
            for row in results:
                domain = Domain(row[1], row[2])
                domain.domain_id = row[0]
                domains.append(domain)
        if page_number > 1:
            previous_page = page_number - 1
        if len(domains) > 0 and (len(domains) >= page_size):
            next_page = page_number + 1
        return domains, previous_page, next_page
        
    def edit_domain(self, updated_domain):
        try:
            with self.__get_cursor() as cursor:
                cursor.execute('UPDATE domains SET domain=:domain, domain_description=:domain_desc WHERE domain_id=:domain_id', domain=updated_domain.domain, domain_desc=updated_domain.domain_description, domain_id=updated_domain.domain_id)
        except oracledb.IntegrityError as e:
            raise CannotFindObject('Domain does not exist')
        
    def del_domain(self, domain_id):
        try:
            with self.__get_cursor() as cursor:
                cursor.execute('DELETE FROM domains WHERE domain_id=:domain_id', domain_id=domain_id)
        except oracledb.IntegrityError as e:
            raise CannotFindObject('Domain does not exist')
        
    def del_domain_for_unit_test(self, domain):
        try:
            with self.__get_cursor() as cursor:
                cursor.execute('DELETE FROM domains WHERE domain=:domain', domain=domain)
        except oracledb.IntegrityError as e:
            raise CannotFindObject('Domain does not exist')
    
    # Course Functions
    def add_course(self, course):
        try:
            with self.__get_cursor() as cursor:
                cursor.execute("INSERT INTO courses (course_id, course_title, theory_hours, lab_hours, work_hours, description, domain_id, term_id) VALUES(:course_id, :course_title, :theory_hours, :lab_hours, :work_hours, :description, :domain_id, :term_id)", 
                               course_id=course.course_id, course_title=course.course_title, theory_hours=course.theory_hours, lab_hours=course.lab_hours, work_hours=course.work_hours, description=course.description, domain_id=course.domain_id, term_id=course.term_id)
        except oracledb.IntegrityError as e:
            raise ObjectAlreadyExists('Course already exists')
    
    def edit_course(self, course):
        try:
            with self.__get_cursor() as cursor:
                cursor.execute("UPDATE courses SET course_title=:course_title,theory_hours=:theory_hours,lab_hours=:lab_hours,work_hours=:work_hours,description=:description,domain_id=:domain_id,term_id=:term_id where course_id=:course_id",
                                course_title=course.course_title, theory_hours=course.theory_hours, lab_hours=course.lab_hours, work_hours=course.work_hours, description=course.description, domain_id=course.domain_id, term_id=course.term_id, course_id=course.course_id)
        except oracledb.IntegrityError as e:
            raise CannotFindObject('Course does not exist')

    def get_course(self, course_id):
        try:
            with self.__get_cursor() as cursor:
                results = cursor.execute('SELECT course_id, course_title, theory_hours, lab_hours, work_hours, description, domain_id, term_id FROM courses WHERE course_id=:course_id', course_id=course_id)
                for row in results:
                    course = Course(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
                    return course
        except oracledb.IntegrityError as e:
            return None
    
    def get_courses(self):
        courses = []
        with self.__get_cursor() as cursor:
            results = cursor.execute('SELECT course_id, course_title, theory_hours, lab_hours, work_hours, description, domain_id, term_id FROM courses ORDER BY term_id, course_id')
            for row in results:
                course = Course(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
                courses.append(course)
        return courses
        
    def get_courses_for_api(self, page_size, page_number):
        courses = []
        previous_page = None
        next_page = None
        offset = (page_number - 1) * page_size
        with self.__get_cursor() as cursor:
            results = cursor.execute('SELECT course_id, course_title, theory_hours, lab_hours, work_hours, description, domain_id, term_id FROM courses ORDER BY term_id, course_id OFFSET :offset ROWS FETCH NEXT :page_size ROWS ONLY', 
                                        offset=offset, page_size=page_size)
            for row in results:
                course = Course(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
                courses.append(course)
        if page_number > 1:
            previous_page = page_number - 1
        if len(courses) > 0 and (len(courses) >= page_size):
            next_page = page_number + 1
        return courses, previous_page, next_page
        
    def del_course(self, course_id):
        try:
            with self.__get_cursor() as cursor:
                cursor.execute('DELETE FROM courses WHERE course_id=:course_id', course_id=course_id)
        except oracledb.IntegrityError as e:
            raise CannotFindObject('Course does not exist')
    
    # Competency Functions
    def add_competency(self, competency):
        try:
            with self.__get_cursor() as cursor:
                cursor.execute("INSERT INTO competencies (competency_id, competency, competency_achievement, competency_type) VALUES(:competency_id, :competency, :competency_achievement, :competency_type)", 
                               competency_id=competency.competency_id, competency=competency.competency, competency_achievement=competency.competency_achievement, competency_type=competency.competency_type)
        except oracledb.IntegrityError as e:
            raise ObjectAlreadyExists('Competency already exists')
    
    def get_competency(self, competency_id):
        try:
            with self.__get_cursor() as cursor:
                results = cursor.execute('SELECT competency_id, competency, competency_achievement, competency_type FROM competencies WHERE competency_id=:competency_id', competency_id=competency_id)
                for row in results:
                    competency = Competency(row[0], row[1], row[2], row[3])
                    return competency
        except oracledb.IntegrityError as e:
            return None
    
    def get_competencies(self):
        competencies = []
        with self.__get_cursor() as cursor:
            results = cursor.execute('SELECT competency_id, competency, competency_achievement, competency_type FROM competencies ORDER BY competency_id')
            for row in results:
                competency = Competency(row[0], row[1], row[2], row[3])
                competencies.append(competency)
        return competencies
    
    def get_competencies_for_api(self, page_size, page_number):
        competencies = []
        previous_page = None
        next_page = None
        offset = (page_number - 1) * page_size
        with self.__get_cursor() as cursor:
            results = cursor.execute('SELECT competency_id, competency, competency_achievement, competency_type FROM competencies ORDER BY competency_id OFFSET :offset ROWS FETCH NEXT :page_size ROWS ONLY',
                                        offset=offset, page_size=page_size)
            for row in results:
                competency = Competency(row[0], row[1], row[2], row[3])
                competencies.append(competency)
        if page_number > 1:
            previous_page = page_number - 1
        if len(competencies) > 0 and (len(competencies) >= page_size):
            next_page = page_number + 1
        return competencies, previous_page, next_page
    
    def edit_competency(self, updated_competency):
        try:
            with self.__get_cursor() as cursor:
                cursor.execute('UPDATE competencies SET competency=:competency, competency_achievement=:competency_achievement, competency_type=:competency_type WHERE competency_id=:competency_id', 
                               competency=updated_competency.competency, competency_achievement=updated_competency.competency_achievement, competency_type=updated_competency.competency_type, competency_id=updated_competency.competency_id)
        except oracledb.IntegrityError as e:
            raise CannotFindObject('Competency does not exist')
        
    def del_competency(self, competency_id):
        try:
            with self.__get_cursor() as cursor:
                cursor.execute('DELETE FROM competencies WHERE competency_id=:competency_id', competency_id=competency_id)
        except oracledb.IntegrityError as e:
            raise CannotFindObject('Competency does not exist')

    # Element Functions
    def add_element(self, element):
        try:
            with self.__get_cursor() as cursor:
                cursor.execute("INSERT INTO elements (element_order, element, element_criteria, competency_id) VALUES(:element_order, :element, :element_criteria, :competency_id)", 
                               element_order=element.element_order, element=element.element, element_criteria=element.element_criteria, competency_id=element.competency_id)
        except oracledb.IntegrityError as e:
            raise ObjectAlreadyExists('Element already exists')
    
    def get_element(self, element_id):
        try:
            with self.__get_cursor() as cursor:
                results = cursor.execute('SELECT element_order, element, element_criteria, competency_id FROM elements WHERE element_id=:element_id', element_id=element_id)
                for row in results:
                    element = Element(row[0], row[1], row[2], row[3])
                    element.element_id = element_id
                    return element
        except oracledb.IntegrityError as e:
            return None
    
    def get_elements(self):
        elements = []
        with self.__get_cursor() as cursor:
            results = cursor.execute('SELECT element_id, element_order, element, element_criteria, competency_id FROM elements ORDER BY competency_id, element_id')
            for row in results:
                element = Element(row[1], row[2], row[3], row[4])
                element.element_id = row[0]
                elements.append(element)
        return elements
    
    def get_elements_of_competency(self, competency_id):
        elements = []
        with self.__get_cursor() as cursor:
            results = cursor.execute('SELECT element_id, element_order, element, element_criteria, competency_id FROM elements WHERE competency_id=:competency_id ORDER BY competency_id, element_id', competency_id=competency_id)
            for row in results:
                element = Element(row[1], row[2], row[3], row[4])
                element.element_id = row[0]
                elements.append(element)
        return elements

    def get_competency_elements_for_api(self, competency_id, page_size, page_number):
        elements = []
        previous_page = None
        next_page = None
        offset = (page_number - 1) * page_size
        with self.__get_cursor() as cursor:
            results = cursor.execute('SELECT element_id, element_order, element, element_criteria, competency_id FROM elements WHERE competency_id=:competency_id ORDER BY competency_id OFFSET :offset ROWS FETCH NEXT :page_size ROWS ONLY',
                                        competency_id=competency_id, offset=offset, page_size=page_size)
            for row in results:
                element = Element(row[1], row[2], row[3], row[4])
                element.element_id = row[0]
                elements.append(element)
        
        if page_number > 1:
            previous_page = page_number - 1
        if len(elements) > 0 and (len(elements) >= page_size):
            next_page = page_number + 1
        return elements, previous_page, next_page
    
    def get_elements_for_api(self, page_size, page_number):
        elements = []
        previous_page = None
        next_page = None
        offset = (page_number - 1) * page_size
        with self.__get_cursor() as cursor:
            results = cursor.execute('SELECT element_id, element_order, element, element_criteria, competency_id FROM elements ORDER BY competency_id, element_id OFFSET :offset ROWS FETCH NEXT :page_size ROWS ONLY',
                                        offset=offset, page_size=page_size)
            for row in results:
                element = Element(row[1], row[2], row[3], row[4])
                element.element_id = row[0]
                elements.append(element)
        
        if page_number > 1:
            previous_page = page_number - 1
        if len(elements) > 0 and (len(elements) >= page_size):
            next_page = page_number + 1
        return elements, previous_page, next_page

    def get_latest_element(self):
        try:
            with self.__get_cursor() as cursor:
                results = cursor.execute('SELECT element_id, element_order, element, element_criteria, competency_id FROM elements ORDER BY element_id DESC FETCH FIRST 1 ROW ONLY')
                
                for row in results:
                    element = Element(row[1], row[2], row[3], row[4])
                    element.element_id = row[0]
                    return element
        except oracledb.Error as e:
            return None

    def edit_element(self, updated_element):
        try:
            with self.__get_cursor() as cursor:
                cursor.execute('UPDATE elements SET element_order=:element_order, element=:element, element_criteria=:element_criteria, competency_id=:competency_id WHERE element_id=:element_id', 
                               element_order=updated_element.element_order, element=updated_element.element, element_criteria=updated_element.element_criteria, competency_id=updated_element.competency_id, element_id=updated_element.element_id)
        except oracledb.IntegrityError as e:
            raise CannotFindObject('Element does not exist')
        
    def del_element(self, element_id):
        try:
            with self.__get_cursor() as cursor:
                cursor.execute('DELETE FROM elements WHERE element_id=:element_id', element_id=element_id)
        except oracledb.IntegrityError as e:
            raise CannotFindObject('Element does not exist')
        
    def del_element_for_unit_test(self, course_id, element, element_hours):
        try:
            with self.__get_cursor() as cursor:
                cursor.execute('DELETE FROM courses_elements WHERE course_id=:course_id and element_hours=:element_hours',
                               course_id=course_id, element_hours=element_hours)
                cursor.execute('DELETE FROM elements WHERE element=:element', element=element)
        except oracledb.IntegrityError as e:
            raise CannotFindObject('Element does not exist')
        
    # Courses & Elements (Bridging)
    def add_course_elements(self, course_id, element_id, element_hours):
        try:
            with self.__get_cursor() as cursor:
                cursor.execute("INSERT INTO courses_elements (course_id, element_id, element_hours) VALUES(:course_id, :element_id, :element_hours)", 
                               course_id=course_id, element_id=element_id, element_hours=element_hours)
        except oracledb.IntegrityError as e:
            raise ObjectAlreadyExists('Courses & Elements already exists')
        
    def get_elements_of_course(self, course_id):
        elements_of_course = []
        with self.__get_cursor() as cursor:
            results = cursor.execute('SELECT element_id, element_order, element, element_criteria, competency_id FROM courses_elements JOIN elements USING(element_id) WHERE course_id=:course_id ORDER BY competency_id, element_id', course_id=course_id)
            for row in results:
                element_of_course = Element(row[1], row[2], row[3], row[4])
                element_of_course.element_id = row[0]
                elements_of_course.append(element_of_course)
        return elements_of_course
    
    def get_course_elements_for_api(self, course_id, competency_id, page_size, page_number):
        elements = []
        previous_page = None
        next_page = None
        offset = (page_number - 1) * page_size
        with self.__get_cursor() as cursor:
            results = cursor.execute('SELECT element_id, element_order, element, element_criteria, competency_id FROM elements JOIN courses_elements USING(element_id) WHERE course_id=:course_id AND competency_id=:competency_id ORDER BY competency_id, element_id OFFSET :offset ROWS FETCH NEXT :page_size ROWS ONLY',
                                        course_id=course_id, competency_id=competency_id, offset=offset, page_size=page_size)
            for row in results:
                element = Element(row[1], row[2], row[3], row[4])
                element.element_id = row[0]
                elements.append(element)
        
        if page_number > 1:
            previous_page = page_number - 1
        if len(elements) > 0 and (len(elements) >= page_size):
            next_page = page_number + 1
        return elements, previous_page, next_page
        
    def get_courses_of_element(self, element_id):
        courses_of_element = []
        with self.__get_cursor() as cursor:
            results = cursor.execute('SELECT course_id, course_title, theory_hours, lab_hours, work_hours, description, domain_id, term_id FROM courses_elements JOIN courses USING(course_id) WHERE element_id=:element_id ORDER BY term_id, course_id', element_id=element_id)
            for row in results:
                course_of_element = Course(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
                courses_of_element.append(course_of_element)
        return courses_of_element
    
    def get_course_element_hours(self, course_id):
        element_hour_pairings = []
        with self.__get_cursor() as cursor:
            results = cursor.execute('SELECT element_id, element_hours FROM courses_elements WHERE course_id=:course_id', course_id=course_id)
            for row in results:
                pairing = (row[0], row[1])
                element_hour_pairings.append(pairing)
        return element_hour_pairings
        
    def get_course_element_groupings(self):
        element_hour_groupings = []
        with self.__get_cursor() as cursor:
            results = cursor.execute('SELECT term_id, course_id, course_title, element_id, element, element_hours, competency_id FROM courses_elements JOIN courses USING(course_id) JOIN elements USING(element_id) ORDER BY term_id, course_id')
            for row in results:
                grouping = (row[1], row[2], row[3], row[4], row[5], row[6])
                element_hour_groupings.append(grouping)
            return element_hour_groupings
        
    def edit_elements_of_course(self, course_id, new_element_id, new_element_hours):
        try:
            with self.__get_cursor() as cursor:
                cursor.execute('UPDATE courses_elements SET element_id=:new_element_id, element_hours=:new_element_hours WHERE course_id=:course_id', 
                               new_element_id=new_element_id, new_element_hours=new_element_hours, course_id=course_id)
        except oracledb.IntegrityError as e:
            raise CannotFindObject('Course does not exist or does not have any elements')
        
    def edit_courses_of_element(self, element_id, new_course_id):
        try:
            with self.__get_cursor() as cursor:
                cursor.execute('UPDATE courses_elements SET course_id=:new_course_id WHERE element_id=:element_id', 
                               new_course_id=new_course_id, element_id=element_id)
        except oracledb.IntegrityError as e:
            raise CannotFindObject('Element does not exist or does not have any courses')
        
    def edit_course_element_hours(self, course_id, element_id, new_hours):
        try:
            with self.__get_cursor() as cursor:
                cursor.execute('UPDATE courses_elements SET element_hours=:new_hours WHERE course_id=:course_id AND element_id=:element_id',
                               new_hours=new_hours, course_id=course_id, element_id=element_id)
        except oracledb.IntegrityError as e:
            raise CannotFindObject('Course or element does not exist')
        
    def del_elements_of_course(self, course_id):
        try:
            with self.__get_cursor() as cursor:
                cursor.execute('DELETE FROM courses_elements WHERE course_id=:course_id', course_id=course_id)
        except oracledb.IntegrityError as e:
            raise CannotFindObject('Course does not exist')
        
    def del_courses_of_element(self, element_id):
        try:
            with self.__get_cursor() as cursor:
                cursor.execute('DELETE FROM courses_elements WHERE element_id=:element_id', element_id=element_id)
        except oracledb.IntegrityError as e:
            raise CannotFindObject('Element does not exist')
        
    def del_course_element_pairing(self, course_id, element_id):
        try:
            with self.__get_cursor() as cursor:
                cursor.execute('DELETE FROM courses_elements WHERE course_id=:course_id AND element_id=:element_id',
                               course_id=course_id, element_id=element_id)
        except oracledb.IntegrityError as e:
            raise CannotFindObject('Course or element does not exist')
        
    #Courses & Competencies
    def get_competencies_of_course(self, course_id):
        competencies = []
        with self.__get_cursor() as cursor:
            results = cursor.execute('SELECT DISTINCT competency_id, competency, competency_achievement, competency_type FROM competencies JOIN elements USING(competency_id) JOIN courses_elements USING(element_id) JOIN courses USING(course_id) WHERE course_id=:course_id ORDER BY competency_id', course_id=course_id)
            for row in results:
                competency = Competency(row[0], row[1], row[2], row[3])
                competencies.append(competency)
        return competencies
        
    def get_courses_of_competency(self, competency_id):
        try:
            courses = []
            with self.__get_cursor() as cursor:
                results = cursor.execute('SELECT DISTINCT course_id, course_title, theory_hours, lab_hours, work_hours, description, domain_id, term_id FROM courses JOIN courses_elements USING(course_id) JOIN courses_elements USING(element_id) JOIN competencies USING(competency_id) WHERE course_id=:course_id WHERE competency_id=:competency_id ORDER BY course_id', competency_id=competency_id)
                for row in results:
                    course = Course(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
                    courses.append(course)
            return courses
        except oracledb.IntegrityError as e:
            raise CannotFindObject('Competency does not exist')
        
    def get_course_competency_groupings(self):
        groupings = []
        with self.__get_cursor() as cursor:
            results = cursor.execute('SELECT DISTINCT competency_id, course_id, course_title FROM courses JOIN courses_elements USING(course_id) JOIN elements USING(element_id) JOIN competencies USING(competency_id) ORDER BY competency_id')
            for row in results:
                grouping = (row[0], row[1], row[2])
                groupings.append(grouping)
        return groupings
        
    def get_course_competencies_for_api(self, course_id, page_size, page_number):
        competencies = []
        previous_page = None
        next_page = None
        offset = (page_number - 1) * page_size
        with self.__get_cursor() as cursor:
            results = cursor.execute('SELECT DISTINCT competency_id, competency, competency_achievement, competency_type FROM competencies JOIN elements USING(competency_id) JOIN courses_elements USING(element_id) JOIN courses USING(course_id) WHERE course_id=:course_id ORDER BY competency_id OFFSET :offset ROWS FETCH NEXT :page_size ROWS ONLY',
                                        course_id=course_id, offset=offset, page_size=page_size)
            for row in results:
                competency = Competency(row[0], row[1], row[2], row[3])
                competencies.append(competency)
        if page_number > 1:
            previous_page = page_number - 1
        if len(competencies) > 0 and (len(competencies) >= page_size):
            next_page = page_number + 1
        return competencies, previous_page, next_page
    
    #Competencies & Elements
    def get_elements_of_competency(self, competency_id):
        elements_of_competency = []
        with self.__get_cursor() as cursor:
            results = cursor.execute('SELECT element_id, element_order, element, element_criteria, competency_id FROM elements WHERE competency_id=:competency_id ORDER BY competency_id, element_id', competency_id=competency_id)
            for row in results:
                element_of_competency = Element(row[1], row[2], row[3], row[4])
                element_of_competency.element_id = row[0]
                elements_of_competency.append(element_of_competency)
        return elements_of_competency 
        
    #Course & Domain
    def get_domain_of_course(self, course_id):
        try:
            with self.__get_cursor() as cursor:
                results = cursor.execute('SELECT domain_id, domain, domain_description FROM domains JOIN courses USING(domain_id) WHERE course_id=:course_id', course_id=course_id)
                for row in results:
                    domain = Domain(row[1], row[2])
                    domain.domain_id = row[0]
                    return domain
        except oracledb.IntegrityError as e:
            raise CannotFindObject('Course does not exist')
        
    #Search Results
    def get_search_results(self, query):
        query = '%' + query + '%'
        course_results = []
        competency_results = []
        element_results = []
        domain_results = []
        
        try:
            with self.__get_cursor() as cursor:
                results = cursor.execute('SELECT course_id, course_title FROM courses JOIN terms USING(term_id) WHERE UPPER(course_id) LIKE UPPER(:query) OR UPPER(course_title) LIKE UPPER(:query) OR UPPER(description) LIKE UPPER(:query) OR UPPER(domain_id) LIKE UPPER(:query) OR UPPER(term_name) LIKE UPPER(:query) ORDER BY term_id, course_id', query=query)
                for row in results:
                    course_result = (row[0], row[1])
                    course_results.append(course_result)
        except oracledb.Error as e:
            course_results = None
            
        try:
            with self.__get_cursor() as cursor:
                results = cursor.execute('SELECT competency_id, competency FROM competencies WHERE UPPER(competency_id) LIKE UPPER(:query) OR UPPER(competency) LIKE UPPER(:query) OR UPPER(competency_achievement) LIKE UPPER(:query) OR UPPER(competency_type) LIKE UPPER(:query) ORDER BY competency_id', query=query)
                for row in results:
                    competency_result = (row[0], row[1])
                    competency_results.append(competency_result)
        except oracledb.Error as e:
            competency_results = None
            
        try:
            with self.__get_cursor() as cursor:
                results = cursor.execute('SELECT element_id, element, competency_id FROM elements WHERE UPPER(element) LIKE UPPER(:query) OR UPPER(element_criteria) LIKE UPPER(:query) OR UPPER(competency_id) LIKE UPPER(:query) ORDER BY competency_id', query=query)
                for row in results:
                    element_result = (row[0], row[1], row[2])
                    element_results.append(element_result)
        except oracledb.Error as e:
            element_results = None
            
        try:
            with self.__get_cursor() as cursor:
                results = cursor.execute('SELECT domain_id, domain FROM domains WHERE UPPER(domain) LIKE UPPER(:query) OR UPPER(domain_description) LIKE UPPER(:query) ORDER BY domain_id', query=query)
                for row in results:
                    domain_result = (row[0], row[1])
                    domain_results.append(domain_result)
        except oracledb.Error as e:
            domain_results = None
        
        return [course_results, competency_results, element_results, domain_results]
        
    def close(self):
        '''Closes the connection'''
        if self.__connection is not None:
            self.__connection.close()
            self.__connection = None

    def __get_cursor(self):
            for i in range(3):
                try:
                    return self.__connection.cursor()
                except Exception as e:
                    # Might need to reconnect
                    self.__reconnect()

    def __reconnect(self):
        try:
            self.close()
        except oracledb.Error as f:
            pass
        self.__connection = self.__connect()

    def __connect(self):
        return oracledb.connect(user=os.environ['DBUSER'], password=os.environ['DBPWD'],
                                             host="198.168.52.211", port=1521, service_name="pdbora19c.dawsoncollege.qc.ca")

if __name__ == '__main__':
    print('Provide file to initialize database')
    file_path = input()
    if os.path.exists(file_path):
        db = Database()
        db.run_file(file_path)
        db.close()
    else:
        print('Invalid Path')
