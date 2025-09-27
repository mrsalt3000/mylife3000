#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
from typing import Dict, List, Optional
from questions_data import (
    QUESTIONS_SELF_KNOWLEDGE, QUESTIONS_VECTOR, QUESTIONS_CHALLENGES,
    QUESTIONS_ENVIRONMENT, QUESTIONS_INTEGRATION, QUESTIONS_MEMORIES
)


class Questionary:
    """Класс для управления вопросами с возможностью dependency injection"""
    
    def __init__(self):
        self.sections: Dict[str, Dict[str, List[str]]] = {}
        self.section_descriptions: Dict[str, str] = {}
        self._load_questions()
    
    def _load_questions(self) -> None:
        """Загружает все вопросы в память"""
        # Основные разделы вопросов
        self.sections = {
            "Самопознание: Кто Я?": QUESTIONS_SELF_KNOWLEDGE,
            "Вектор: Куда я движусь?": QUESTIONS_VECTOR,
            "Вызовы: Что мне мешает?": QUESTIONS_CHALLENGES,
            "Окружение: Мои отношения?": QUESTIONS_ENVIRONMENT,
            "Интеграция: Как я живу?": QUESTIONS_INTEGRATION,
            "Капсула Времени: История для моих детей": QUESTIONS_MEMORIES
        }
        
        # Описания разделов
        self.section_descriptions = {
            "Самопознание: Кто Я?": "Самопознание: Кто Я? - это вопросы, помогающие понять свою личность, ценности и убеждения",
            "Вектор: Куда я движусь?": "Вектор: Куда я движусь? - вопросы о целях, мечтах и направлении жизни",
            "Вызовы: Что мне мешает?": "Вызовы: Что мне мещается? - вопросы о трудностях, страхах и ограничениях",
            "Окружение: Мои отношения?": "Окружение: Мои отношения? - вопросы о взаимодействии с людьми и социальной среде",
            "Интеграция: Как я живу?": "Интеграция: Как я живу? - вопросы о повседневной жизни, привычках и ритуалах",
            "Капсула Времени: История для моих детей": "Капсула Времени: История для моих детей - это то, что мы можем оставить себе будущему и потомкам"
        }
        
        # Добавляем пункт "Случайный вопрос" в каждый раздел
        for section_name, questions_dict in self.sections.items():
            questions_dict["Случайный вопрос"] = []
            for theme_questions in questions_dict.values():
                if isinstance(theme_questions, list):
                    questions_dict["Случайный вопрос"].extend(theme_questions)
    
    def get_section_questions(self, section_name: str) -> Optional[Dict[str, List[str]]]:
        """Возвращает вопросы для указанного раздела"""
        return self.sections.get(section_name)
    
    def get_section_description(self, section_name: str) -> str:
        """Возвращает описание раздела"""
        return self.section_descriptions.get(section_name, "")
    
    def get_random_question(self, section_name: str, theme: Optional[str] = None) -> Optional[str]:
        """Возвращает случайный вопрос из раздела/темы"""
        questions_dict = self.get_section_questions(section_name)
        if not questions_dict:
            return None
        
        if theme and theme in questions_dict:
            return random.choice(questions_dict[theme])
        elif "Случайный вопрос" in questions_dict and questions_dict["Случайный вопрос"]:
            return random.choice(questions_dict["Случайный вопрос"])
        else:
            # Если нет специальной категории, выбираем из всех вопросов раздела
            all_questions = []
            for theme_questions in questions_dict.values():
                if isinstance(theme_questions, list):
                    all_questions.extend(theme_questions)
            return random.choice(all_questions) if all_questions else None
    
    def get_themes(self, section_name: str) -> List[str]:
        """Возвращает список тем для раздела (исключая 'Случайный вопрос')"""
        questions_dict = self.get_section_questions(section_name)
        if not questions_dict:
            return []
        
        return [key for key in questions_dict.keys() if key != "Случайный вопрос"]
    
    def get_all_sections(self) -> List[str]:
        """Возвращает список всех разделов"""
        return list(self.sections.keys())