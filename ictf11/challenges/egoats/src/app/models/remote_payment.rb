class RemotePayment < ActiveRecord::Base
  has_one :payment
  belongs_to :user
  attr_accessible nil
  before_create :default_values

  def default_values
    self.token = rand(36**8).to_s(36)
  end

  def start
    # Are there other cubicles left in the world, except the one I'm sitting?
    # Maaan, I feel so alone..
    # NOTE: PayBro call should be here
  end

  def completed?
    # PayBro guarantees to terminate all transactions in less than 6 seconds.
    Time.now - self.created_at > 5.seconds
  end

  def status?
    # NOTE: check PayBro status here
    true
  end
end
