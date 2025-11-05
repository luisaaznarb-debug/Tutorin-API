# -*- coding: utf-8 -*-
"""
tests/test_reading_system.py
Tests para el sistema de comprensión lectora
"""

import pytest
from logic.ai_reading.question_parser import parse_questions, validate_questions, _detect_question_type


class TestQuestionParser:
    """Tests para el parser de preguntas"""

    def test_parse_numbered_questions(self):
        """Test de parseo con preguntas numeradas"""
        text = """
        1. ¿Cuál es la idea principal del texto?
        2. ¿Qué significa la palabra "extinto"?
        3. ¿Por qué desaparecieron los dinosaurios?
        """
        questions = parse_questions(text)

        assert len(questions) == 3
        assert "idea principal" in questions[0]["q"]
        assert "significa" in questions[1]["q"]
        assert "por qué" in questions[2]["q"].lower()

    def test_parse_lettered_questions(self):
        """Test de parseo con preguntas con letras"""
        text = """
        a) ¿Dónde vivían los dinosaurios?
        b) ¿Cuándo se extinguieron?
        c) ¿Quién descubrió el primer fósil?
        """
        questions = parse_questions(text)

        assert len(questions) == 3
        assert all(q["q"].endswith("?") for q in questions)

    def test_parse_bullet_questions(self):
        """Test de parseo con viñetas"""
        text = """
        • ¿Qué tipos de dinosaurios existían?
        • ¿Cómo se alimentaban?
        - ¿Dónde encontramos fósiles?
        """
        questions = parse_questions(text)

        assert len(questions) == 3

    def test_parse_questions_without_numbers(self):
        """Test de parseo sin numeración"""
        text = """
        ¿Cuál es la idea principal?
        ¿Qué significa herbívoro?
        ¿Por qué eran tan grandes?
        """
        questions = parse_questions(text)

        assert len(questions) == 3

    def test_detect_main_idea_type(self):
        """Test de detección de tipo: idea principal"""
        assert _detect_question_type("¿Cuál es la idea principal del texto?") == "main_idea"
        assert _detect_question_type("¿De qué trata el texto?") == "main_idea"
        assert _detect_question_type("¿Cuál es el tema principal?") == "main_idea"

    def test_detect_vocabulary_type(self):
        """Test de detección de tipo: vocabulario"""
        assert _detect_question_type("¿Qué significa la palabra extinto?") == "vocabulary"
        assert _detect_question_type("¿Qué quiere decir herbívoro?") == "vocabulary"
        assert _detect_question_type("¿Cuál es la definición de fósil?") == "vocabulary"

    def test_detect_inference_type(self):
        """Test de detección de tipo: inferencia"""
        assert _detect_question_type("¿Por qué crees que desaparecieron?") == "inference"
        assert _detect_question_type("¿Qué opinas sobre este tema?") == "inference"
        assert _detect_question_type("¿Por qué razón eran tan grandes?") == "inference"

    def test_detect_detail_type(self):
        """Test de detección de tipo: detalle"""
        assert _detect_question_type("¿Cuándo vivieron los dinosaurios?") == "detail"
        assert _detect_question_type("¿Dónde encontramos fósiles?") == "detail"
        assert _detect_question_type("¿Quién descubrió el primer fósil?") == "detail"
        assert _detect_question_type("¿Cuántos tipos de dinosaurios había?") == "detail"

    def test_validate_valid_questions(self):
        """Test de validación de preguntas válidas"""
        questions = [
            {"q": "¿Cuál es la idea principal?", "answer": "", "type": "main_idea"},
            {"q": "¿Qué significa extinto?", "answer": "", "type": "vocabulary"}
        ]
        assert validate_questions(questions) is True

    def test_validate_invalid_questions(self):
        """Test de validación de preguntas inválidas"""
        # Sin pregunta
        assert validate_questions([]) is False

        # Pregunta vacía
        questions = [{"q": "", "answer": "", "type": "comprehension"}]
        assert validate_questions(questions) is False

        # Pregunta muy corta
        questions = [{"q": "¿Qué?", "answer": "", "type": "comprehension"}]
        assert validate_questions(questions) is False

    def test_parse_mixed_formats(self):
        """Test de parseo con formatos mixtos"""
        text = """
        1. ¿Cuál es la idea principal?
        a) ¿Qué significa extinto?
        • ¿Por qué desaparecieron?
        ¿Dónde vivían?
        """
        questions = parse_questions(text)

        assert len(questions) == 4
        assert all(q["type"] in ["main_idea", "vocabulary", "inference", "detail"] for q in questions)


class TestReadingEngine:
    """Tests para verificar compatibilidad con reading_engine"""

    def test_exercise_format(self):
        """Test del formato de ejercicio esperado"""
        exercise = {
            "text": "Los dinosaurios fueron animales fascinantes que vivieron hace millones de años.",
            "questions": [
                {"q": "¿Cuándo vivieron los dinosaurios?", "answer": "Hace millones de años", "type": "detail"}
            ]
        }

        assert "text" in exercise
        assert "questions" in exercise
        assert len(exercise["questions"]) > 0
        assert "q" in exercise["questions"][0]
        assert "answer" in exercise["questions"][0]
        assert "type" in exercise["questions"][0]


# Tests de integración (requieren mock de OpenAI)
# Estos tests se pueden ejecutar manualmente o con mocks

@pytest.mark.skip(reason="Requiere API key de OpenAI")
class TestWithOpenAI:
    """Tests que requieren API de OpenAI (ejecutar manualmente)"""

    @pytest.mark.asyncio
    async def test_generate_text(self):
        """Test de generación de texto"""
        from logic.ai_reading.text_generator import generate_text_with_gpt4

        text = await generate_text_with_gpt4("dinosaurios", "3")

        assert text
        assert len(text.split()) >= 50

    @pytest.mark.asyncio
    async def test_generate_questions(self):
        """Test de generación de preguntas"""
        from logic.ai_reading.question_generator import generate_questions_with_gpt4

        text = "Los dinosaurios fueron animales que vivieron hace millones de años. Había muchos tipos diferentes, como el T-Rex y el Triceratops. Se extinguieron después de que un meteorito chocara con la Tierra."

        questions = await generate_questions_with_gpt4(text, "3")

        assert len(questions) == 4
        assert all("q" in q and "answer" in q and "type" in q for q in questions)

    @pytest.mark.asyncio
    async def test_generate_answers(self):
        """Test de generación de respuestas"""
        from logic.ai_reading.answer_generator import generate_answers_for_questions

        text = "Los dinosaurios fueron animales que vivieron hace millones de años."
        questions = [
            {"q": "¿Cuándo vivieron los dinosaurios?", "answer": "", "type": "detail"}
        ]

        result = await generate_answers_for_questions(text, questions)

        assert len(result) == 1
        assert result[0]["answer"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
