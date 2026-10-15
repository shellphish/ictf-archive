class CreditCard < ActiveRecord::Base
  validates_uniqueness_of :number, :message => 'This credit card has already been used. We are running low on goat-stock, so only one goat per customer is allowed. Come on, you already have one. Don\'t be greedy'
end
