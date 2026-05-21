/**
 * @description Trigger to validate duplicate Account records based on Phone number.
 *              Prevents insertion of Account if another Account with the same Phone exists.
 * @author Copilot
 * @date 2026-05-20
 */
trigger AccountDuplicatePhoneTrigger on Account (before insert) {

    // Collect all non-blank phone numbers from incoming records
    Set<String> incomingPhoneNumbers = new Set<String>();
    
    for (Account acc : Trigger.new) {
        if (String.isNotBlank(acc.Phone)) {
            incomingPhoneNumbers.add(acc.Phone);
        }
    }

    // If no phone numbers to check, exit early
    if (incomingPhoneNumbers.isEmpty()) {
        return;
    }

    // Query existing Accounts with matching phone numbers
    Map<String, Account> existingAccountsByPhone = new Map<String, Account>();
    
    for (Account existingAcc : [
        SELECT Id, Name, Phone 
        FROM Account 
        WHERE Phone IN :incomingPhoneNumbers
    ]) {
        existingAccountsByPhone.put(existingAcc.Phone, existingAcc);
    }

    // Also check for duplicates within the same batch (bulk insert scenario)
    Map<String, Account> phoneNumbersInBatch = new Map<String, Account>();

    // Validate each incoming record
    for (Account acc : Trigger.new) {
        if (String.isNotBlank(acc.Phone)) {
            // Check against existing records in database
            if (existingAccountsByPhone.containsKey(acc.Phone)) {
                Account duplicateAcc = existingAccountsByPhone.get(acc.Phone);
                acc.addError('Duplicate Account found! An Account with Phone number "' + acc.Phone + 
                             '" already exists: ' + duplicateAcc.Name + ' (Id: ' + duplicateAcc.Id + ')');
            }
            // Check for duplicates within the same batch
            else if (phoneNumbersInBatch.containsKey(acc.Phone)) {
                acc.addError('Duplicate Phone number "' + acc.Phone + 
                             '" found within the same batch. Please use unique phone numbers.');
            }
            else {
                // Track this phone number for intra-batch duplicate detection
                phoneNumbersInBatch.put(acc.Phone, acc);
            }
        }
    }
}
