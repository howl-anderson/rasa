:desc: Define custom fallback actions with thresholds for NLU and Core for letting
       your conversation fail gracefully with open source dialogue management.

.. _fallback-actions:

Fallback Actions
================

.. edit-link::

.. contents::
   :local:

Sometimes you want to revert to a fallback action, such as replying,
`"Sorry, I didn't understand that"`. You can handle fallback cases by adding appropriate
rules. Rasa Open Source comes with two default implementations of fallbacks. In addition
you can also use :ref:`custom-actions` to implement custom procedures.

Handling Low NLU Confidence
---------------------------

Although the Rasa :ref:`intent-classifier` will generalize to unseen messages, messages
which are too far of from the training data, will lead to a low classification
confidence. In order to handle messages with low confidence we recommend to add the
:ref:`fallback-classifier` to your NLU pipeline. The :ref:`fallback-classifier` will
predict an intent ``nlu_fallback`` whenever no other intent prediction crosses
the configured threshold.

Writing Stories / Rules for Messages with Low Confidence
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When you added the :ref:`fallback-classifier` to your NLU pipeline, you can treat
messages with low classification confidence just as any other intent. The following
:ref:`rule<rules>` will ask the user to rephrase whenever they send a message which is
classified with low confidence:

.. code-block:: yaml

    rules:

    - rule: Ask the user to rephrase whenever they send a message with low NLU confidence
      steps:
      - ...
      - intent: nlu_fallback
      - action: utter_please_rephrase

Using :ref:`rules` or :ref:`stories` you can implement any desired fallback behavior.

.. _two-stage-fallback:

Using the Two-Stage-Fallback
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``Two-Stage-Fallback`` handles low NLU confidence in multiple stages
by trying to disambiguate the user input.

TODO: add rule policy requirement

.. note::

    Before using the ``Two-Stage-Fallback`` you have to make sure to add the
    ``out_of_scope`` intent to your :ref:`domain<domains>`.
    When users send messages with
    an intent ``out_of_scope`` (e.g. by pressing a button) during the fallback,
    Rasa Open Source will know that the users denied the given intent suggestions.

- If a NLU prediction has a low confidence score, the user is asked to affirm
  the classification of the intent.  (Default action:
  ``action_default_ask_affirmation``)

    - If they affirm by sending a message with high NLU confidence (e.g. by pressing
      a button), the story continues as if the intent was classified
      with high confidence from the beginning.
    - If they deny by sending a message with the intent ``out_of_scope``, the user is
      asked to rephrase their message.

- Rephrasing  (default action: ``action_default_ask_rephrase``)

    - If the classification of the rephrased intent was confident, the story
      continues as if the user had this intent from the beginning.
    - If the rephrased intent was not classified with high confidence, the user
      is asked to affirm the classified intent.

- Second affirmation  (default action: ``action_default_ask_affirmation``)

    - If they affirm by sending a message with high NLU confidence (e.g. by pressing
      a button), the story continues as if the user had this intent from the beginning.
    - If the user denies by sending a message with the intent ``out_of_scope``, the
      original intent is classified as the specifies ``deny_suggestion_intent_name``,
      and an ultimate fallback action ``fallback_nlu_action_name`` is
      triggered (e.g. a handoff to a human).

Rasa Open Source provides the default implementations of
``action_default_ask_affirmation`` and ``action_default_ask_rephrase``.
The default implementation of ``action_default_ask_rephrase`` action utters
the response ``utter_ask_rephrase``, so be sure to specify this
response in your domain file.
The implementation of both actions can be overwritten with
:ref:`custom actions <custom-actions>`.

To use the ``Two-Stage-Fallback`` for messages with low NLU confidence, add the
following :ref:`rule<rules>` to your training data:

.. code-block:: yaml

    rules:

    - rule: Implementation of the Two-Stage-Fallback
      steps:
      - ...
      - intent: nlu_fallback
      - action: two_stage_fallback
      - form: two_stage_fallback

Handling Low Core Confidence
----------------------------

Similar as users might send unexpected messages which lead to low NLU confidences,
their actions might lead users on unknown conversation paths. Rasa's machine
learning policies such as the :ref:`ted_policy` are optimized to handle these unknown
paths. To handle cases where even the machine learning policies can't predict the
next action with confidence, make sure to add the :ref:`rule-policy` to your
policy configuration. The :ref:`rule-policy` will predict a default action with a
configurable confidence in case no matching rule was found. If none of the other
:ref:`policies` had a higher prediction confidence the assistant will run this default
action.

You can configure the action which is run in case low of Core confidence as well as
the threshold for this as follows:

.. code-block:: yaml

  policies:
    - name: RulePolicy
      # Confidence threshold for the `fallback_action_name` to apply.
      # The action will apply if no other action was predicted with
      # a confidence >= core_fallback_threshold
      core_fallback_threshold: 0.4
      fallback_action_name: "action_default_fallback"


``action_default_fallback`` is a default action in Rasa Core which sends the
``utter_default`` response to the user. Make sure to specify
the ``utter_default`` in your domain file. It will also revert back to the
state of the conversation before the user message that caused the
fallback, so that it will not influence the prediction of future actions.
You can take a look at the source of the action below:

.. autoclass:: rasa.core.actions.action.ActionDefaultFallback


You can also create your own custom action to use as a fallback (see
:ref:`custom actions <custom-actions>` for more info on custom actions).
