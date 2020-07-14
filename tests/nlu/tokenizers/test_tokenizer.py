import pytest

from rasa.nlu.constants import TEXT, INTENT, RESPONSE, TOKENS_NAMES, MESSAGE_ACTION_NAME, ACTION_TEXT
from rasa.nlu.training_data import Message, TrainingData
from rasa.nlu.tokenizers.whitespace_tokenizer import WhitespaceTokenizer


def test_tokens_comparison():
    from rasa.nlu.tokenizers.tokenizer import Token

    x = Token("hello", 0)
    y = Token("Hello", 0)

    assert x == x
    assert y < x

    assert x != 1

    with pytest.raises(TypeError):
        assert y < "a"


@pytest.mark.parametrize(
    "text, expected_tokens, expected_indices",
    [("Forecast for lunch", ["Forecast", "for", "lunch"], [(0, 8), (9, 12), (13, 18)])],
)
def test_train_tokenizer(text, expected_tokens, expected_indices):
    tk = WhitespaceTokenizer()

    message = Message(text)
    message.set(RESPONSE, text)
    message.set(INTENT, text)

    training_data = TrainingData()
    training_data.training_examples = [message]

    tk.train(training_data)

    for attribute in [RESPONSE, TEXT]:
        tokens = training_data.training_examples[0].get(TOKENS_NAMES[attribute])

        assert [t.text for t in tokens] == expected_tokens
        assert [t.start for t in tokens] == [i[0] for i in expected_indices]
        assert [t.end for t in tokens] == [i[1] for i in expected_indices]

    # check intent attribute
    tokens = training_data.training_examples[0].get(TOKENS_NAMES[INTENT])

    assert [t.text for t in tokens] == [text]


@pytest.mark.parametrize(
    "text, expected_tokens, expected_indices",
    [("Forecast for lunch", ["Forecast", "for", "lunch"], [(0, 8), (9, 12), (13, 18)])],
)
def test_train_tokenizer_e2e_actions(text, expected_tokens, expected_indices):
    tk = WhitespaceTokenizer()

    message = Message(text)
    message.set(ACTION_TEXT, text)
    message.set(MESSAGE_ACTION_NAME, text)

    training_data = TrainingData()
    training_data.training_examples = [message]

    tk.train(training_data)

    for attribute in [ACTION_TEXT, TEXT]:
        tokens = training_data.training_examples[0].get(TOKENS_NAMES[attribute])

        assert [t.text for t in tokens] == expected_tokens
        assert [t.start for t in tokens] == [i[0] for i in expected_indices]
        assert [t.end for t in tokens] == [i[1] for i in expected_indices]


@pytest.mark.parametrize(
    "text, expected_tokens, expected_indices",
    [("Forecast for lunch", ["Forecast", "for", "lunch"], [(0, 8), (9, 12), (13, 18)])],
)
def test_train_tokenizer_action_name(text, expected_tokens, expected_indices):
    tk = WhitespaceTokenizer()

    message = Message(text)
    message.set(MESSAGE_ACTION_NAME, text)

    training_data = TrainingData()
    training_data.training_examples = [message]

    tk.train(training_data)

    # check action_name attribute
    tokens = training_data.training_examples[0].get(TOKENS_NAMES[MESSAGE_ACTION_NAME])

    assert [t.text for t in tokens] == [text]


@pytest.mark.parametrize(
    "text, expected_tokens, expected_indices",
    [("Forecast for lunch", ["Forecast", "for", "lunch"], [(0, 8), (9, 12), (13, 18)])],
)
def test_process_tokenizer(text, expected_tokens, expected_indices):
    tk = WhitespaceTokenizer()

    message = Message(text)

    tk.process(message)

    tokens = message.get(TOKENS_NAMES[TEXT])

    assert [t.text for t in tokens] == expected_tokens
    assert [t.start for t in tokens] == [i[0] for i in expected_indices]
    assert [t.end for t in tokens] == [i[1] for i in expected_indices]


@pytest.mark.parametrize(
    "text, expected_tokens",
    [("action_listen", ["action","listen"])],
)
def test_process_tokenizer_action_name(text, expected_tokens):
    tk = WhitespaceTokenizer()

    message = Message(text)
    message.set(MESSAGE_ACTION_NAME, text)

    tk.process(message, MESSAGE_ACTION_NAME)

    tokens = message.get(TOKENS_NAMES[MESSAGE_ACTION_NAME])

    assert [t.text for t in tokens] == expected_tokens


@pytest.mark.parametrize(
    "text, expected_tokens",
    [("I am hungry", ["I","am", "hungry"])],
)
def test_process_tokenizer_action_test(text, expected_tokens):
    tk = WhitespaceTokenizer()

    message = Message(text)
    message.set(MESSAGE_ACTION_NAME, text)
    message.set(ACTION_TEXT, text)

    tk.process(message, ACTION_TEXT)

    tokens = message.get(TOKENS_NAMES[ACTION_TEXT])
    assert [t.text for t in tokens] == expected_tokens

    message.set(ACTION_TEXT, "")
    tk.process(message, MESSAGE_ACTION_NAME)
    tokens = message.get(TOKENS_NAMES[MESSAGE_ACTION_NAME])
    assert [t.text for t in tokens] == [text]


@pytest.mark.parametrize(
    "text, expected_tokens",
    [
        ("Forecast_for_LUNCH", ["Forecast_for_LUNCH"]),
        ("Forecast for LUNCH", ["Forecast for LUNCH"]),
    ],
)
def test_split_intent(text, expected_tokens):
    component_config = {"intent_tokenization_flag": True, "intent_split_symbol": "+"}

    tk = WhitespaceTokenizer(component_config)

    message = Message(text)
    message.set(INTENT, text)

    assert [t.text for t in tk._split_intent(message)] == expected_tokens


@pytest.mark.parametrize(
    "text, expected_tokens",
    [
        ("Forecast_for_LUNCH", ["Forecast_for_LUNCH"]),
        ("Forecast for LUNCH", ["Forecast for LUNCH"]),
        ("Forecast+for+LUNCH", ["Forecast", "for", "LUNCH"])
    ],
)
def test_split_action_name(text, expected_tokens):
    component_config = {"intent_tokenization_flag": True, "intent_split_symbol": "+"}

    tk = WhitespaceTokenizer(component_config)

    message = Message(text)
    message.set(MESSAGE_ACTION_NAME, text)

    assert [t.text for t in tk._split_action(message)] == expected_tokens
