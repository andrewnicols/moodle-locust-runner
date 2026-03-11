@locust
Feature: Create test situation for Locust to run
  In order to facilitate performance testing
  As Moodle HQ
  We shoudl create test data for Locust jobs to consume

  Scenario: Create Locust test data
    Given the following "users" exist:
      | username    |
      | testuser1   |
      | testuser2   |
      | testuser3   |
      | testuser4   |
      | testuser5   |
      | testuser6   |
      | testuser7   |
      | testuser8   |
      | testuser9   |
      | testuser10  |
      | testuser11  |
      | testuser12  |
      | testuser13  |
      | testuser14  |
      | testuser15  |
      | testuser16  |
      | testuser17  |
      | testuser18  |
      | testuser19  |
      | testuser20  |
      | testuser21  |
      | testuser22  |
      | testuser23  |
      | testuser24  |
      | testuser25  |
      | testuser26  |
      | testuser27  |
      | testuser28  |
      | testuser29  |
      | testuser30  |
      | testuser31  |
      | testuser32  |
      | testuser33  |
      | testuser34  |
      | testuser35  |
      | testuser36  |
      | testuser37  |
      | testuser38  |
      | testuser39  |
      | testuser40  |
      | testuser41  |
      | testuser42  |
      | testuser43  |
      | testuser44  |
      | testuser45  |
      | testuser46  |
      | testuser47  |
      | testuser48  |
      | testuser49  |
      | testuser50  |
      | testuser51  |
      | testuser52  |
      | testuser53  |
      | testuser54  |
      | testuser55  |
      | testuser56  |
      | testuser57  |
      | testuser58  |
      | testuser59  |
      | testuser60  |
      | testuser61  |
      | testuser62  |
      | testuser63  |
      | testuser64  |
      | testuser65  |
      | testuser66  |
      | testuser67  |
      | testuser68  |
      | testuser69  |
      | testuser70  |
      | testuser71  |
      | testuser72  |
      | testuser73  |
      | testuser74  |
      | testuser75  |
      | testuser76  |
      | testuser77  |
      | testuser78  |
      | testuser79  |
      | testuser80  |
      | testuser81  |
      | testuser82  |
      | testuser83  |
      | testuser84  |
      | testuser85  |
      | testuser86  |
      | testuser87  |
      | testuser88  |
      | testuser89  |
      | testuser90  |
      | testuser91  |
      | testuser92  |
      | testuser93  |
      | testuser94  |
      | testuser95  |
      | testuser96  |
      | testuser97  |
      | testuser98  |
      | testuser99  |
      | testuser100 |
    And the following "courses" exist:
      | fullname | shortname |
      | Course 1 | C1        |
    And the following "course enrolments" exist:
      | user        | course | role    |
      | testuser1   | C1     | student |
      | testuser2   | C1     | student |
      | testuser3   | C1     | student |
      | testuser4   | C1     | student |
      | testuser5   | C1     | student |
      | testuser6   | C1     | student |
      | testuser7   | C1     | student |
      | testuser8   | C1     | student |
      | testuser9   | C1     | student |
      | testuser10  | C1     | student |
      | testuser11  | C1     | student |
      | testuser12  | C1     | student |
      | testuser13  | C1     | student |
      | testuser14  | C1     | student |
      | testuser15  | C1     | student |
      | testuser16  | C1     | student |
      | testuser17  | C1     | student |
      | testuser18  | C1     | student |
      | testuser19  | C1     | student |
      | testuser20  | C1     | student |
      | testuser21  | C1     | student |
      | testuser22  | C1     | student |
      | testuser23  | C1     | student |
      | testuser24  | C1     | student |
      | testuser25  | C1     | student |
      | testuser26  | C1     | student |
      | testuser27  | C1     | student |
      | testuser28  | C1     | student |
      | testuser29  | C1     | student |
      | testuser30  | C1     | student |
      | testuser31  | C1     | student |
      | testuser32  | C1     | student |
      | testuser33  | C1     | student |
      | testuser34  | C1     | student |
      | testuser35  | C1     | student |
      | testuser36  | C1     | student |
      | testuser37  | C1     | student |
      | testuser38  | C1     | student |
      | testuser39  | C1     | student |
      | testuser40  | C1     | student |
      | testuser41  | C1     | student |
      | testuser42  | C1     | student |
      | testuser43  | C1     | student |
      | testuser44  | C1     | student |
      | testuser45  | C1     | student |
      | testuser46  | C1     | student |
      | testuser47  | C1     | student |
      | testuser48  | C1     | student |
      | testuser49  | C1     | student |
      | testuser50  | C1     | student |
      | testuser51  | C1     | student |
      | testuser52  | C1     | student |
      | testuser53  | C1     | student |
      | testuser54  | C1     | student |
      | testuser55  | C1     | student |
      | testuser56  | C1     | student |
      | testuser57  | C1     | student |
      | testuser58  | C1     | student |
      | testuser59  | C1     | student |
      | testuser60  | C1     | student |
      | testuser61  | C1     | student |
      | testuser62  | C1     | student |
      | testuser63  | C1     | student |
      | testuser64  | C1     | student |
      | testuser65  | C1     | student |
      | testuser66  | C1     | student |
      | testuser67  | C1     | student |
      | testuser68  | C1     | student |
      | testuser69  | C1     | student |
      | testuser70  | C1     | student |
      | testuser71  | C1     | student |
      | testuser72  | C1     | student |
      | testuser73  | C1     | student |
      | testuser74  | C1     | student |
      | testuser75  | C1     | student |
      | testuser76  | C1     | student |
      | testuser77  | C1     | student |
      | testuser78  | C1     | student |
      | testuser79  | C1     | student |
      | testuser80  | C1     | student |
      | testuser81  | C1     | student |
      | testuser82  | C1     | student |
      | testuser83  | C1     | student |
      | testuser84  | C1     | student |
      | testuser85  | C1     | student |
      | testuser86  | C1     | student |
      | testuser87  | C1     | student |
      | testuser88  | C1     | student |
      | testuser89  | C1     | student |
      | testuser90  | C1     | student |
      | testuser91  | C1     | student |
      | testuser92  | C1     | student |
      | testuser93  | C1     | student |
      | testuser94  | C1     | student |
      | testuser95  | C1     | student |
      | testuser96  | C1     | student |
      | testuser97  | C1     | student |
      | testuser98  | C1     | student |
      | testuser99  | C1     | student |
      | testuser100 | C1     | student |
    And the following "activities" exist:
      | activity   | name                   | intro                         | course | idnumber    |
      | assign     | Test assignment name   | Test assignment description   | C1     | assign1     |
      | book       | Test book name         | Test book description         | C1     | book1       |
      | choice     | Test choice name       | Test choice description       | C1     | choice1     |
      | data       | Test database name     | Test database description     | C1     | data1       |
      | feedback   | Test feedback name     | Test feedback description     | C1     | feedback1   |
      | folder     | Test folder name       | Test folder description       | C1     | folder1     |
      | forum      | Test forum name        | Test forum description        | C1     | forum1      |
      | glossary   | Test glossary name     | Test glossary description     | C1     | glossary1   |
      | imscp      | Test imscp name        | Test imscp description        | C1     | imscp1      |
      | label      | Test label name        | Test label description        | C1     | label1      |
      | lesson     | Test lesson name       | Test lesson description       | C1     | lesson1     |
      | lti        | Test lti name          | Test lti description          | C1     | lti1        |
      | page       | Test page name         | Test page description         | C1     | page1       |
      | quiz       | Test quiz name         | Test quiz description         | C1     | quiz1       |
      | resource   | Test resource name     | Test resource description     | C1     | resource1   |
      | scorm      | Test scorm name        | Test scorm description        | C1     | scorm1      |
      | url        | Test url name          | Test url description          | C1     | url1        |
      | wiki       | Test wiki name         | Test wiki description         | C1     | wiki1       |
      | workshop   | Test workshop name     | Test workshop description     | C1     | workshop1   |
