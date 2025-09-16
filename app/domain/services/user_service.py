from datetime import datetime
from ..models.user.entities import User

from ..models.application.entities import Area, Diagnosis, EpidemicFocus, Doctor
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
        admin_exists = User.query.filter_by(user_type='admin').first()
        if not admin_exists:
            try:
                admin = User(
                    login='admin',
                    name='admin',
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
                    db.session.add(Area(name_area=area_name))

            # 2. Заполнение эпидемических групп
            epidemic_groups = ["I", "II", "III", "IV", "V", "безадресные"]
            for group_name in epidemic_groups:
                if not EpidemicFocus.query.filter_by(name=group_name).first():
                    db.session.add(EpidemicFocus(name=group_name))

            # 3. Заполнение диагнозов
            diagnoses_data = [
                {"mkb_code": "A15", "name": "A15 - Туберкулез органов дыхания, подтвержденный бактериологически и гистологически"},
                {"mkb_code": "A16", "name": "A16 - Туберкулез органов дыхания, не подтвержденный бактериологически или гистологически"},
                {"mkb_code": "A17", "name": "A17 - Туберкулез нервной системы"},
                {"mkb_code": "A18", "name": "A18 - Туберкулез других органов"},
                {"mkb_code": "A19", "name": "A19 - Милиарный туберкулез"},
                {"mkb_code": "Z03", "name": "Z03 - Медицинское наблюдение и оценка при подозрении на заболевание или патологическое состояние"},
                {"mkb_code": "Z20.1", "name": "Z20.1 - Контакт с больным и возможность заражения туберкулезом"},
                {"mkb_code": "Y58.0", "name": "Y58.0 - Осложнения от введения вакцины БЦЖ"},
                {"mkb_code": "R76.1", "name": "R76.1 - Аномальная реакция на туберкулиновую пробу"},
                {"mkb_code": "B90", "name": "B90 - Отдаленные последствия туберкулеза"},
            ]
            for diagnosis in diagnoses_data:
                if not Diagnosis.query.filter_by(mkb_code=diagnosis["mkb_code"]).first():
                    db.session.add(Diagnosis(**diagnosis))

            db.session.commit()
            return True

        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to fill directories: {str(e)}")


class UserService:
    """Сервис для работы с пользователями"""

    @staticmethod
    def create_user(user_data):
        """
        Создает нового пользователя
        Args:
            user_data (dict): {
                "login": str,
                "name": str,
                "password": str,
                "user_type": str (admin, doctor, disinfector и т.п.)
            }
        Returns:
            User
        """
        try:
            user = User(
                login =user_data['login'],
                name =user_data['name'],
                password_hash=generate_password_hash(user_data['password']),
                user_type=user_data['user_type']
            )
            db.session.add(user)
            db.session.commit()
            return user

        except Exception as e:
            db.session.rollback()
            raise Exception(f"User creation failed: {str(e)}")

    @staticmethod
    def get_user_by_id(user_id):
        """Возвращает пользователя по ID"""
        return User.query.get(user_id)

    @staticmethod
    def update_user(user_id, update_data):
        """
        Обновляет данные пользователя
        Args:
            user_id (int)
            update_data (dict)
        """
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found")

        try:
            for key, value in update_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)

            db.session.commit()
            return user

        except Exception as e:
            db.session.rollback()
            raise Exception(f"User update failed: {str(e)}")
