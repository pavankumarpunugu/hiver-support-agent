Results from the actual run (59 messages, 1 dropped for missing text).
Raw classification_report output, kept for transparency alongside REPORT.md.

=== Agent (NOTE: not a real measurement — true_intent was copied from
suggested_intent due to skipped human review under time pressure; see
REPORT.md Section 4) ===
                      precision    recall  f1-score   support

      account_access       1.00      1.00      1.00         6
billing_subscription       1.00      1.00      1.00        12
     device_platform       1.00      1.00      1.00         3
     feature_request       1.00      1.00      1.00        15
       general_other       1.00      1.00      1.00        16
  playback_technical       1.00      1.00      1.00         7

            accuracy                           1.00        59
           macro avg       1.00      1.00      1.00        59
        weighted avg       1.00      1.00      1.00        59

=== Trivial baseline (real, independently computed) ===
                      precision    recall  f1-score   support

      account_access       0.00      0.00      0.00         6
billing_subscription       0.00      0.00      0.00        12
     device_platform       0.00      0.00      0.00         3
     feature_request       0.25      1.00      0.41        15
       general_other       0.00      0.00      0.00        16
  playback_technical       0.00      0.00      0.00         7

            accuracy                           0.25        59
           macro avg       0.04      0.17      0.07        59
        weighted avg       0.06      0.25      0.10        59

=== Simple baseline (real, independently computed) ===
                      precision    recall  f1-score   support

      account_access       1.00      0.50      0.67         6
billing_subscription       0.80      0.67      0.73        12
     device_platform       0.33      0.67      0.44         3
     feature_request       1.00      0.13      0.24        15
       general_other       0.37      0.81      0.51        16
  playback_technical       0.67      0.29      0.40         7

            accuracy                           0.51        59
           macro avg       0.70      0.51      0.50        59
        weighted avg       0.72      0.51      0.48        59
