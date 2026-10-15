require 'time' # That's always true. Day of release is coming too soon.

class PaymentsController < ApplicationController
  # TODO: add kick-ass security

  def show
    # Eh, not a good idea.
  end

  def new
    @payment = Payment.new
    @payment.credit_card = CreditCard.new
    @payment.user = current_user
    @credit_card = @payment.credit_card
  end

  def create
    # It's raining MONEY!
    @payment = Payment.new params[:payment]
    @payment.user = current_user
    @credit_card = ActiveMerchant::Billing::CreditCard.new(params[:payment][:credit_card_attributes] )
    @credit_card.require_verification_value = false
    unless @credit_card.valid?
      render :action => "new" and return
    end

    if @credit_card.valid? and @payment.save and @payment.credit_card.save
      # Dude's legit.
      session[:payment_id] = @payment.id
      redirect_to :action => :start_remote_payment and return
    end
    # Learn how to type, bro.
    render :action => "new" and return
  end

 def start_remote_payment
        # Create our proxy object
        @payment= Payment.find(session[:payment_id])
        @payment.remote_payment = RemotePayment.new
        @payment.remote_payment.user = current_user
        @payment.remote_payment.save
        @payment.save

        # Submit payment to PayBro
        @payment.remote_payment.start

        # Annnnd, grab a soda. Or coffee? Definitely coffee.
        redirect_to :action => :poll_remote_payment and return
 end

  def poll_remote_payment

    @payment = Payment.find(session[:payment_id])
    unless @payment.remote_payment.completed?
      # PayBro needs more time, chill
      return
    end
    if @payment.remote_payment.status?
      redirect_to :action => :payment_successful and return
    end
      redirect_to :action => :payment_failed and return
  end

 def payment_successful
     # My ears are bleeding for the extreme happyness I'm experiencing
     @payment= Payment.find(session[:payment_id])
 end
 def payment_failed
     @payment= Payment.find(session[:payment_id])
     # We are fined $1 for each failed transaction. This dude will pay for this.
     # TODO: Implement revenge.
 end

end
