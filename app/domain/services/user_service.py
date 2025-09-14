from datetime import datetime
from ..models.user.entities import Administrator, Doctor, Disinfector, Area, UserIDCounter

from ..models.application.entities import Diagnosis, EpidemicFocus
from ...core.extensions import db
from werkzeug.security import generate_password_hash

class UserInitializer:
    """Сервис для инициализации пользователей и справочников"""
    
    @staticmethod
    def create_admin_account():
        """
        Создает учетную запись администратора по умолчанию
        если она не существует
        """
        admin_exists = Administrator.query.filter_by(login='admin').first()
        if not admin_exists:
            try:
                admin = Administrator(
                    name='Admin',
                    login='admin',
                    password_hash=generate_password_hash('admin123'),
                    user_type='admin'
                )
                db.session.add(admin)
                db.session.commit()
                return True
            except Exception as e:
                db.session.rollback()
                raise Exception(f"Failed to create admin account: {str(e)}")
        return False

    @staticmethod
    def fill_directories():
        """
        Заполняет системные справочники начальными данными:
        - Участки
        - Эпидемические группы
        - Диагнозы
        """
        try:
            # 1. Заполнение участков
            areas = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "ДПДО", "РПТД"]
            for area_name in areas:
                if not Area.query.filter_by(name_area=area_name).first():
                    area = Area(name_area=area_name)
                    db.session.add(area)
            
            # 2. Заполнение эпидемических групп
            epidemic_groups = ["I", "II", "III", "IV", "V", "безадресные"]
            for group_name in epidemic_groups:
                if not EpidemicFocus.query.filter_by(name=group_name).first():
                    group = EpidemicFocus(name=group_name)
                    db.session.add(group)
            
            # 3. Заполнение диагнозов
            diagnoses_data = [
                {"mkb_code": "A15", "name": "A15 - Туберкулез органов дыхания, подтвержденный бактериологически и гистологически"}, {"mkb_code": "A16", "name": "A16 - Туберкулез органов дыхания, не подтвержденный бактериологически или гистологически"}, {"mkb_code": "A17", "name": "A17 - Туберкулез нервной системы"}, {"mkb_code": "A18", "name": "A18 - Туберкулез других органов"}, {"mkb_code": "A19", "name": "A19 - Милиарный туберкулез"}, {"mkb_code": "Z03", "name": "Z03 - Медицинское наблюдение и оценка при подозрении на заболевание или патологическое состояние"}, {"mkb_code": "Z20.1", "name": "Z20.1 - Контакт с больным и возможность заражения туберкулезом"}, {"mkb_code": "Y58.0", "name": "Y58.0 - Осложнения от введения вакцины БЦЖ"}, {"mkb_code": "R76.1", "name": "R76.1 - Аномальная реакция на туберкулиновую пробу"}, {"mkb_code": "B90", "name": "B90 - Отдаленные последствия туберкулеза"}
            ]
            
            for diagnosis in diagnoses_data:
                if not Diagnosis.query.filter_by(mkb_code=diagnosis["mkb_code"]).first():
                    new_diagnosis = Diagnosis(
                        mkb_code=diagnosis["mkb_code"],
                        name=diagnosis["name"]
                    )
                    db.session.add(new_diagnosis)
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to fill directories: {str(e)}")

    @staticmethod
    def initialize_user_id_counter():
        """
        Инициализирует счетчик ID пользователей если он не существует
        """
        if not UserIDCounter.query.first():
            counter = UserIDCounter(last_id=0)
            db.session.add(counter)
            db.session.commit()
            return True
        return False


class UserService:
    """Сервис для работы с пользователями"""
    
    @staticmethod
    def create_user(user_data):
        """
        Создает нового пользователя в зависимости от типа
        Args:
            user_data (dict): Данные пользователя
        Returns:
            User: Созданный пользователь
        """
        try:
            user_class = {
                'doctor': Doctor,
                'disinfector': Disinfector,
                'admin': Administrator
            }.get(user_data['user_type'], Disinfector)
            
            user = user_class(
                name=user_data['name'],
                login=user_data['login'],
                password_hash=generate_password_hash(user_data['password']),
                user_type=user_data['user_type']
            )
            
            if user_data['user_type'] == 'doctor':
                user.area_id = user_data.get('area_id')
            
            db.session.add(user)
            db.session.commit()
            return user
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"User creation failed: {str(e)}")

    @staticmethod
    def get_user_by_id(user_id):
        """
        Получает пользователя по ID
        Args:
            user_id (int): ID пользователя
        Returns:
            User: Найденный пользователь или None
        """
        user = Doctor.query.get(user_id)
        if not user:
            user = Disinfector.query.get(user_id)
        if not user:
            user = Administrator.query.get(user_id)
        return user

    @staticmethod
    def update_user(user_id, update_data):
        """
        Обновляет данные пользователя
        Args:
            user_id (int): ID пользователя
            update_data (dict): Данные для обновления
        Returns:
            User: Обновленный пользователь
        """
        user = UserService.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        try:
            # Исключаем специальные поля из общего цикла
            special_fields = ['area_id']  # можно добавить другие при необходимости
            
            for key, value in update_data.items():
                if key in special_fields:
                    continue  # эти поля обрабатываются отдельно
                    
                if hasattr(user, key):
                    setattr(user, key, value)
            
            # Обработка специальных полей
            if 'area_id' in update_data:
                user.area_id = update_data['area_id']
            
            db.session.commit()
            return user
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"User update failed: {str(e)}")