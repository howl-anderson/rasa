:desc: Follow a rule-based process of information gathering using FormActions
       in open source bot framework Rasa.

.. _forms:

Forms
=====

.. edit-link::

.. note::
   There is an in-depth tutorial
   `here <https://blog.rasa.com/building-contextual-assistants-with-rasa-formaction/>`_
   about how to use Rasa Forms for slot filling.

TODO: Where to add deprecation for formpolicy? is the migration guide enough?

.. contents::
   :local:

One of the most common conversation patterns is to collect a few pieces of
information from a user in order to do something (book a restaurant, call an
API, search a database, etc.). This is also called **slot filling**.

Usage
-----

To use forms with Rasa Open Source you need to make sure that the :ref:`rule-policy` is
added to your policy configuration. For example:

.. code-block:: yaml

  policies:
    - ... # other policies
    - name: RulePolicy

Defining a Form
~~~~~~~~~~~~~~~

Define a form by adding it to the ``forms`` section in your :ref:`domain<domains>`.
The name of the form is also the name action of the action which you can use in
:ref:`stories` or :ref:`rules` to handle form executions. Further you need to define
:ref:`forms-slot-mappings` for each slot which your form should fill. You can specify
one or more slot mappings for each slot to be filled.

The following example of a form ``your_form`` will fill only one slot
``age`` from an extracted entity ``age``.

.. code-block:: yaml

  forms:
    your_form:
      age:
      - type: from_entity
        entity: age

Once the form action gets called for the first time, the form gets activated and will
start asking the user for the next slot which is not already set. It does this by
looking for a response called ``utter_ask_{slot_name}``, so you need to define these in
your domain file for each required slot.

TODO: explain using custom action for asking

Activating a Form
~~~~~~~~~~~~~~~~~

To activate a form you need to add add a :ref:`story<stories>` or :ref:`rule<rules>`
which describes when the assistant should run the form. In case a certain intent
triggers a form you can for example use the following rule:

.. code-block:: yaml

    - rule: Activate form
      steps:
      - ...
      - intent: intent_which_activates_form
      - action: your_form
      - form: your_form

.. note::

    The ``form: your_form`` step indicates that the form should be activated after
    ``your_form`` was run.

.. _forms-slot-mappings:

Slot Mappings
~~~~~~~~~~~~~

Rasa Open Source comes with four predefined functions to fill the slots of a form
based on the latest user message. Please see :ref:`forms-custom-slot-mappings` if
you need a custom function to extract the required information.

from_entity
^^^^^^^^^^^

The ``from_entity`` mapping fills slots based on extracted entities.
It will look for an entity called ``entity_name`` to fill a slot ``slot_name``
regardless of user intent if ``intent_name`` is ``None`` else only if the users intent
is ``intent_name``. If ``role_name`` and/or ``group_name`` are provided, the role/group
label of the entity also needs to match the given values. The slot mapping will not
apply if the intent of the last message is ``excluded_intent``. Note that you can
define also define lists of intents for ``intent`` and ``not_intent``.

.. code-block:: yaml

  forms:
    your_form:
      slot_name:

      - type: from_entity
        entity: entity_name
        role: role_name
        group: group name
        intent: intent_name
        not_intent: excluded_intent

from_text
^^^^^^^^^

The ``from_text`` mapping will use the text of the next user utterance to fill the slot
``slot_name`` regardless of user intent if ``intent_name`` is ``None`` else only if
user intent is ``intent_name``. The slot mapping will not
apply if the intent of the last message is ``excluded_intent``. Note that you can
define also define lists of intents for ``intent`` and ``not_intent``.

.. code-block:: yaml

  forms:
    your_form:
      slot_name:

      - type: from_text
        intent: intent_name
        not_intent: excluded_intent

from_intent
^^^^^^^^^^^

The ``from_intent`` mapping will fill slot ``slot_name`` with value ``my_value`` if
user intent is ``intent_name`` or ``None``. The slot mapping will not
apply if the intent of the last message is ``excluded_intent``. Note that you can
define also define lists of intents for ``intent`` and ``not_intent``.

.. note::

    The slot mapping will not apply during the initial activation of the form. To fill
    a slot based on the intent which activated the form use the ``from_trigger_intent``
    mapping

.. code-block:: yaml

  forms:
    your_form:
      slot_name:

      - type: from_intent
        value: my_value
        intent: intent_name
        not_intent: excluded_intent

from_trigger_intent
^^^^^^^^^^^^^^^^^^^

The ``from_trigger_intent`` mapping will fill slot ``slot_name`` with value ``my_value``
if the form was activated by a user message with intent ``intent_name``.
The slot mapping will not apply if the intent of the last message is
``excluded_intent``. Note that you can define also define lists of intents for
``intent`` and ``not_intent``.

.. code-block:: yaml

  forms:
    your_form:
      slot_name:

      - type: from_trigger_intent
        value: my_value
        intent: intent_name
        not_intent: excluded_intent


Writing Stories / Rules for Unhappy Form Paths
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Explain how featurize / unfeaturize stuff?

Advanced Usage
--------------

Forms are fully customizable using :ref:`custom-actions`.

Validating Form input
~~~~~~~~~~~~~~~~~~~~~

After extracting a slot value from user input, you can validate the extracted slots.
By default Rasa Open Source only validates if any slot was filled after requesting
a slot. If nothing is extracted from the user’s utterance for any of the required slots,
an ActionExecutionRejection error will be raised, meaning the action execution was
rejected and therefore Core will fall back onto a different policy to predict another
action.

You can implement a :ref:`custom action<custom-actions>` ``action_validate_{form_name}``
to validate any extracted slots. Make sure to add this action to the ``actions``
section of your domain:

.. code-block:: yaml

  actions:
  - ... # other actions
  - action_validate_my_form

When the form is executed it will run your custom action. In your custom action
you can either

- validate already extracted slots. You can retrieve them from the tracker by running
  ``tracker.get_extracted_slots``.
- use :ref:`forms-custom-slot-mappings` to extract slot values .

After validating the extracted slots, return ``SlotSet`` events for them. If you want
to mark a slot as invalid return a ``SlotSet`` event which sets the value to ``None``.
Note that if you don't return a ``SlotSet`` for an extracted slot, Rasa Open Source
will assume that the value is valid.

The following example shows the implementation of a custom action
which validates that every extracted slot has a value.

.. code-block:: python

    from typing import Dict, Text, List, Any

    from rasa_sdk import Tracker
    from rasa_sdk.events import EventType
    from rasa_sdk.executor import CollectingDispatcher
    from rasa_sdk import Action
    from rasa_sdk.events import SlotSet


    class ValidateSlots(Action):
        def name(self) -> Text:
            return "action_validate_my_form"

        def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
        ) -> List[EventType]:
            extracted_slots: Dict[Text, Any] = tracker.get_extracted_slots()

            validation_events = []

            for slot_name, slot_value in extracted_slots:
                # Simply validation which checks if the extracted slot has a value
                if slot_value is not None:
                    validation_events.append(SlotSet(slot_name, slot_value))
                else:
                    # Return a `SlotSet` event with value `None` to indicate that this
                    # slot still needs to be filled.
                    validation_events.append(SlotSet(slot_name, None))

            return validation_events


.. _forms-custom-slot-mappings:

Custom Slot Mappings
~~~~~~~~~~~~~~~~~~~~

If none of the predefined :ref:`forms-slot-mappings` fit your use case, you can use the
:ref:`custom action<custom-actions>` ``action_validate_{form_name}`` to write your own
extraction code. Rasa Open Source will trigger this function when the form is run.

Make sure your custom action returns ``SlotSet`` events for every extracted value.
The following example shows the implementation of a custom slot mapping which sets
a slot based on the length of the last user message.

.. code-block:: python

    from typing import Dict, Text, List

    from rasa_sdk import Tracker
    from rasa_sdk.events import EventType
    from rasa_sdk.executor import CollectingDispatcher
    from rasa_sdk import Action
    from rasa_sdk.events import SlotSet


    class ValidateSlots(Action):
        def name(self) -> Text:
            return "action_validate_my_form"

        def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
        ) -> List[EventType]:
            text_of_last_user_message = tracker.latest_message.get("text")

            return [SlotSet("user_message_length", text_of_last_user_message)]


Requesting Extra Slots
~~~~~~~~~~~~~~~~~~~~~~

If you have frequent changes to the required slots and don't want to retrain your
assistant when something changes, you can also use a
:ref:`custom action<custom-actions>` ``action_validate_{form_name}`` to define
which slot should be requested. Rasa Open Source will run your custom action whenever
the form is executed. Set the slot ``requested_slot`` to the name of the slot which
should be extracted next. If all desired slots are filled, set ``requested_slot``
to ``None``.

The following example shows the implementation of a custom action which requests
the three slots ``last_name``, ``first_name``, and ``city``.

.. code-block:: python

    from typing import Dict, Text, List

    from rasa_sdk import Tracker
    from rasa_sdk.events import EventType
    from rasa_sdk.executor import CollectingDispatcher
    from rasa_sdk import Action
    from rasa_sdk.events import SlotSet


    class ValidateSlots(Action):
        def name(self) -> Text:
            return "action_validate_my_form"

        def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
        ) -> List[EventType]:
            required_slots = ["last name", "first_name", "city"]

            for slot_name in required_slots:
                if tracker.slots.get(slot_name) is None:
                    # The slot is not filled yet. Request the user to fill this slot next.
                    return [SlotSet("requested_slot", slot_name)]

            # All slots are filled.
            return [SlotSet("requested_slot", None)]


The requested_slot slot
~~~~~~~~~~~~~~~~~~~~~~~

The slot ``requested_slot`` is automatically added to the domain as an
unfeaturized slot. If you want to make it featurized, you need to add it
to your domain file as a categorical slot. You might want to do this if you
want to handle your unhappy paths differently depending on what slot is
currently being asked from the user. For example, say your users respond
to one of the bot's questions with another question, like *why do you need to know that?*
The response to this ``explain`` intent depends on where we are in the story.
In the restaurant case, your stories would look something like this:

.. code-block:: story

    ## explain cuisine slot
    * request_restaurant
        - restaurant_form
        - form{"name": "restaurant_form"}
        - slot{"requested_slot": "cuisine"}
    * explain
        - utter_explain_cuisine
        - restaurant_form
        - slot{"cuisine": "greek"}
        ( ... all other slots the form set ... )
        - form{"name": null}

    ## explain num_people slot
    * request_restaurant
        - restaurant_form
        - form{"name": "restaurant_form"}
        - slot{"requested_slot": "num_people"}
    * explain
        - utter_explain_num_people
        - restaurant_form
        - slot{"cuisine": "greek"}
        ( ... all other slots the form set ... )
        - form{"name": null}

Again, it is **strongly** recommended that you use interactive
learning to build these stories.
Please read :ref:`section_interactive_learning_forms`
on how to use interactive learning with forms.

Debugging
---------

The first thing to try is to run your bot with the ``--debug`` flag, see :ref:`command-line-interface` for details.
If you are just getting started, you probably only have a few hand-written stories.
This is a great starting point, but
you should give your bot to people to test **as soon as possible**. One of the guiding principles
behind Rasa Core is:

.. pull-quote:: Learning from real conversations is more important than designing hypothetical ones

So don't try to cover every possibility in your hand-written stories before giving it to testers.
Real user behavior will always surprise you!
