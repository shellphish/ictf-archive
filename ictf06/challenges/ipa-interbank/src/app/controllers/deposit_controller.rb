class DepositController < ApplicationController

    before_filter :login_required

  @@transaction_file = "/var/spool/transactions/ipa"

  def index
    list
    render :action => 'list'
  end

  # GETs should be safe (see http://www.w3.org/2001/tag/doc/whenToUseGet.html)
  verify :method => :post, :only => [ :destroy, :create, :update ],
         :redirect_to => { :action => :list }

  #def list
  #  @deposit_pages, @deposits = paginate :deposits, :per_page => 10
  #end

  def show
    @deposit = Deposit.find(params[:id])
  end

  def new
    @deposit = Deposit.new
    @currencies = currencies_for_select
  end

  def create

    @currencies = currencies_for_select

    if params[:check_id].nil? or params[:check_id].length != 172
      flash[:error] = 'Invalid check ID'
      render :action => 'new' and return
    end

    ccheck = IO.popen("/usr/bin/ccheck #{params[:check_id]}", "r")
    result = ccheck.gets
    ccheck.close
    if result.nil?
      flash[:error] = 'Error running ccheck'
      redirect_to :action => 'new' and return
    end
    if result.to_i == 0
      flash[:error] = "No money to deposit!"
      redirect_to :action => "new" and return
    end
    if result.to_i < 0
      flash[:error] = 'Invalid check ID'
      redirect_to :action => 'new' and return
    end

    currency = Currency.find(params[:currency_id])
    if currency.nil?
        flash[:error] = 'Invalid currency ID'
        redirect_to :action => 'new' and return
    end
    @deposit = Deposit.new({:user_id => current_user.id, :amount => result, :orig_rate => currency.rate, :curr_rate => currency.rate, :currency_id => currency.id})
    if @deposit.save
      flash[:notice] = 'Deposit was successfully created.'
      redirect_to :controller => 'user', :action => 'show_deposits'
    else
      render :action => 'new'
    end
  end

  def edit
    @deposit = Deposit.find(params[:id])
  end

  def update
    @deposit = Deposit.find(params[:id])
    if @deposit.update_attributes(params[:deposit])
      flash[:notice] = 'Deposit was successfully updated.'
      redirect_to :action => 'show', :id => @deposit
    else
      render :action => 'edit'
    end
  end

  def withdraw
    @deposit = Deposit.find(params[:id])
  end

  def destroy
    deposit = Deposit.find(params[:id])
    if deposit.nil? 
        flash[:error] = 'Cannot find the deposit'  
        redirect_to :action => 'withdraw' and return
    elsif params[:iban].length != 172
        flash[:error] = 'Invalid IBAN'
        redirect_to :action => 'withdraw' and return
    end
    amount = deposit.amount * 1 / deposit.curr_rate * deposit.orig_rate
    amount = amount.to_i

    tid = 0 + rand(1000000 - 0)

    fname = "#{@@transaction_file}/trans_#{tid}"
    f = File.new(fname, "w")
    f.puts "#{amount} #{params[:iban]}"
    f.close

    deposit.destroy
    redirect_to :controller => 'user', :action => 'show_deposits', :id => current_user.id
  end

private

  def currencies_for_select
    all_currencies = Currency.find(:all, :select => "symbol, id")
    currencies = Array.new
    all_currencies.each do |currency|
        currencies << [currency.symbol, currency.id]
    end
    return currencies
  end


end
