/**
 * @description Apex class for Account migration operations with AuraEnabled methods
 *              for Lightning Web Components and Aura components.
 * @author Copilot
 * @date 2026-05-20
 */
public with sharing class AccountSFMigration {

    /**
     * @description Creates a new Account record with the provided details.
     * @param name The name of the Account
     * @param billingStreet The billing street address
     * @param billingCity The billing city
     * @param billingState The billing state
     * @param billingPostalCode The billing postal code
     * @param billingCountry The billing country
     * @param phone The phone number of the Account
     * @param accountType The type of the Account
     * @return The Id of the newly created Account
     * @throws AuraHandledException if any error occurs during account creation
     */
    @AuraEnabled
    public static Id createAccount(String name, String billingStreet, String billingCity, 
                                   String billingState, String billingPostalCode, 
                                   String billingCountry, String phone, String accountType) {
        try {
            if (String.isBlank(name)) {
                throw new AuraHandledException('Account Name is required.');
            }

            Account newAccount = new Account();
            newAccount.Name = name;
            newAccount.BillingStreet = billingStreet;
            newAccount.BillingCity = billingCity;
            newAccount.BillingState = billingState;
            newAccount.BillingPostalCode = billingPostalCode;
            newAccount.BillingCountry = billingCountry;
            newAccount.Phone = phone;
            newAccount.Type = accountType;

            insert newAccount;

            return newAccount.Id;
        } catch (DmlException dmlEx) {
            throw new AuraHandledException('Error creating Account: ' + dmlEx.getMessage());
        } catch (Exception ex) {
            throw new AuraHandledException('Unexpected error: ' + ex.getMessage());
        }
    }

    /**
     * @description Creates a new Account record using a wrapper class for cleaner input.
     * @param accountWrapper The wrapper containing account details
     * @return The Id of the newly created Account
     * @throws AuraHandledException if any error occurs during account creation
     */
    @AuraEnabled
    public static Id createAccountFromWrapper(AccountWrapper accountWrapper) {
        try {
            if (accountWrapper == null || String.isBlank(accountWrapper.name)) {
                throw new AuraHandledException('Account Name is required.');
            }

            Account newAccount = new Account();
            newAccount.Name = accountWrapper.name;
            newAccount.BillingStreet = accountWrapper.billingStreet;
            newAccount.BillingCity = accountWrapper.billingCity;
            newAccount.BillingState = accountWrapper.billingState;
            newAccount.BillingPostalCode = accountWrapper.billingPostalCode;
            newAccount.BillingCountry = accountWrapper.billingCountry;
            newAccount.Phone = accountWrapper.phone;
            newAccount.Type = accountWrapper.accountType;

            insert newAccount;

            return newAccount.Id;
        } catch (DmlException dmlEx) {
            throw new AuraHandledException('Error creating Account: ' + dmlEx.getMessage());
        } catch (Exception ex) {
            throw new AuraHandledException('Unexpected error: ' + ex.getMessage());
        }
    }

    /**
     * @description Retrieves a list of Contacts associated with an Account based on Account Number.
     * @param accountNumber The Account Number to search for
     * @return List of Contact records associated with the Account
     * @throws AuraHandledException if any error occurs during retrieval
     */
    @AuraEnabled(cacheable=true)
    public static List<Contact> getContactsByAccountNumber(String accountNumber) {
        try {
            if (String.isBlank(accountNumber)) {
                throw new AuraHandledException('Account Number is required.');
            }

            List<Account> accounts = [
                SELECT Id, Name, AccountNumber 
                FROM Account 
                WHERE AccountNumber = :accountNumber 
                WITH SECURITY_ENFORCED
                LIMIT 1
            ];

            if (accounts.isEmpty()) {
                return new List<Contact>();
            }

            List<Contact> contacts = [
                SELECT Id, FirstName, LastName, Name, Email, Phone, Title, Department, MailingAddress
                FROM Contact 
                WHERE AccountId = :accounts[0].Id
                WITH SECURITY_ENFORCED
                ORDER BY Name ASC
            ];

            return contacts;
        } catch (QueryException queryEx) {
            throw new AuraHandledException('Error querying Contacts: ' + queryEx.getMessage());
        } catch (Exception ex) {
            throw new AuraHandledException('Unexpected error: ' + ex.getMessage());
        }
    }

    /**
     * @description Retrieves a list of Contacts associated with an Account based on Account Id.
     * @param accountId The Account Id to search for
     * @return List of Contact records associated with the Account
     * @throws AuraHandledException if any error occurs during retrieval
     */
    @AuraEnabled(cacheable=true)
    public static List<Contact> getContactsByAccountId(Id accountId) {
        try {
            if (accountId == null) {
                throw new AuraHandledException('Account Id is required.');
            }

            List<Contact> contacts = [
                SELECT Id, FirstName, LastName, Name, Email, Phone, Title, Department, MailingAddress
                FROM Contact 
                WHERE AccountId = :accountId
                WITH SECURITY_ENFORCED
                ORDER BY Name ASC
            ];

            return contacts;
        } catch (QueryException queryEx) {
            throw new AuraHandledException('Error querying Contacts: ' + queryEx.getMessage());
        } catch (Exception ex) {
            throw new AuraHandledException('Unexpected error: ' + ex.getMessage());
        }
    }

    /**
     * @description Wrapper class for Account creation input.
     */
    public class AccountWrapper {
        @AuraEnabled public String name { get; set; }
        @AuraEnabled public String billingStreet { get; set; }
        @AuraEnabled public String billingCity { get; set; }
        @AuraEnabled public String billingState { get; set; }
        @AuraEnabled public String billingPostalCode { get; set; }
        @AuraEnabled public String billingCountry { get; set; }
        @AuraEnabled public String phone { get; set; }
        @AuraEnabled public String accountType { get; set; }
    }
}
