class Payment < ActiveRecord::Base
  belongs_to :user
  belongs_to :remote_payment
  has_one :credit_card
  accepts_nested_attributes_for :credit_card
  validates :amount, :presence => {:message => 'Yeah, we need some money' },  :numericality => { :greater_than => 1 }
end
