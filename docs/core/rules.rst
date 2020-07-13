:desc: TBD.

.. _rules:

Rules
=====

.. edit-link::

.. contents::
   :local:

Rasa rules are a form of training data used to train Rasa's dialogue management models.
Rules describe parts of conversations which should always follow the same path.
Useful applications for rules are for example:

* **FAQs**: FAQs are questions which users ask out of context. Rules are an easy way to
  specify fixed answers to the questions.

* **Fallbacks**: Users might confront your assistant with messages which your assistant
  can't handle yet. Unless these messages are close to existing training data, Rasa
  NLU will typically show low intent confidence levels for these messages. You can
  use :ref:`fallback-classifier` to treat low NLU confidence like an FAQ

* **Forms** (TODO: LINK): It's a common use case for assistants to collect form-like
  data from the user. Both, activation of forms as well as handling of unexpected
  events as part of a form, are usually following fixed paths.

    (OTHER ideas?)

Do we need a rules vs. stories section?

.. note::

    Although rules are a very useful tool for :ref:`rules-use-cases` like FAQs or
    handling messages with low confidence, **we recommend to not overuse rules**.
    If you want to build an advanced assistant which scales with your use cases, you
    should always combine rules with :ref:`stories`. Using :ref:`stories` in
    combination with a machine learning policies, like the :ref:`ted_policy` you can
    train an assistant which is able to handle unexpected story paths and learn from
    real users.

Writing a Rule
--------------

Before you start writing rules, you have to make sure that the RulePolicy (TODO: LINK)
is added to your model configuration:

.. code-block:: yaml

    policies:
    - ... # Other policies
    - name: RulePolicy

TODO: YAML vs. Markdown

Rules for the Conversation Start
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To write a rule which only applies at the beginning of a conversation, start with the
intent which starts the conversations and then add the actions which your assistant
should perform in response to that.

.. code-block:: yaml

    rules:

    - rule: Say `hello` when the user starts a conversation with intent `greet`
      steps:
      - intent: greet
      - action: utter_greet

.. _rules-applying-anytime:

Rules which Apply Anytime
~~~~~~~~~~~~~~~~~~~~~~~~~

To indicate that a rule can apply at any point in a conversation, specify ``...`` as
first conversation step. The ``...`` indicate that the rule applies independent of the
previous conversation.

.. code-block:: yaml

    rules:

    - rule: Say `hello` whenever sends a message with intent `greet`
      steps:
      - ...
      - intent: greet
      - action: utter_greet

This example rule applies at the start of conversation as well as when the user decides
to a send a message with an intent ``greet`` in the middle of an ongoing conversation.

Rules with Pre-Conditions
~~~~~~~~~~~~~~~~~~~~~~~~~

Rules can describe requirements which have to be fulfilled for the rule to be
applicable. To do so, add any information about the prior conversation, before the
``...``:

.. code-block:: yaml

    rules:

    - rule: Only say `hello` when the user provided a name
      steps:
      - slot: user_provided_name
        value: true
      - ...
      - intent: greet
      - action: utter_greet

Rules and Forms
~~~~~~~~~~~~~~~

Rules don't apply when a :ref:`forms` is active. Rules become applicable again if

- the form filled all required slots
- the form rejected its execution (TODO: LINK TO FORM DOCS).

.. _rules-use-cases:

Use Cases
---------

This section explains common use cases of rules.

.. _rules-faqs:

FAQs / Mapping Intents to Actions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Some messages doesn't require context to answer. Common examples are either FAQs
or triggers which are sent by :ref:`reminders-and-external-events`.

To map an intent to a certain action, you need :ref:`rules-applying-anytime`. The
following example always responds with an action ``utter_greet`` in case the user
greets the assistant.

.. code-block:: yaml

    rules:

    - rule: Say `hello` whenever sends a message with intent `greet`
      steps:
      - ...
      - intent: greet
      - action: utter_greet

Failing Gracefully
~~~~~~~~~~~~~~~~~~

Handling unknown messages gracefully is key to a successful assistant. As unknown
messages can happen at any time in a conversation, they are a special case of
:ref:`rules-faqs`. Please see the docs on :ref:`fallback-actions` for different ways to
handle fallbacks gracefully.

Forms
~~~~~

Use :ref:`forms` if you need to collect multiple pieces of information from a user
before being able to process their request. A common example for this is booking a table
at a restaurant which requires information like name, number of people and time.
