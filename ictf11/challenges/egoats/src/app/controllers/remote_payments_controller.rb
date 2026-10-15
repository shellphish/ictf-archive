class RemotePaymentsController < ApplicationController
  # GET /remote_payments
  # GET /remote_payments.json
  def index
    @remote_payments = RemotePayment.all

    respond_to do |format|
      format.html # index.html.erb
      format.json { render :json => @remote_payments }
    end
  end

  # GET /remote_payments/1
  # GET /remote_payments/1.json
  def show
    @remote_payment = RemotePayment.find(params[:id])
    unless @remote_payment.user == current_user:
      redirect_to '/' and return
    end

    respond_to do |format|
      format.html # show.html.erb
      format.json { render :json => @remote_payment }
    end
  end

  # GET /remote_payments/new
  # GET /remote_payments/new.json
  def new
    @remote_payment = RemotePayment.new

    respond_to do |format|
      format.html # new.html.erb
      format.json { render :json => @remote_payment }
    end
  end

  # GET /remote_payments/1/edit
  def edit
    @remote_payment = RemotePayment.find(params[:id])
    unless @remote_payment.user == current_user:
      redirect_to '/' and return
    end
  end

  # POST /remote_payments
  # POST /remote_payments.json
  def create
    @remote_payment = RemotePayment.new(params[:remote_payment])

    respond_to do |format|
      if @remote_payment.save
        format.html { redirect_to @remote_payment, :notice => 'Remote payment was successfully created.' }
        format.json { render :json => @remote_payment, :status => :created, :location => @remote_payment }
      else
        format.html { render :action => "new" }
        format.json { render :json => @remote_payment.errors, :status => :unprocessable_entity }
      end
    end
  end

  # PUT /remote_payments/1
  # PUT /remote_payments/1.json
  def update
    @remote_payment = RemotePayment.find(params[:id])
    unless @remote_payment.user == current_user:
      redirect_to '/' and return
    end

    respond_to do |format|
      if @remote_payment.update_attributes(params[:remote_payment])
        @remote_payment.token = params[:remote_payment][:token]
        @remote_payment.save
        format.html { redirect_to @remote_payment, :notice => 'Remote payment was successfully updated.' }
        format.json { head :ok }
      else
        format.html { render :action => "edit" }
        format.json { render :json => @remote_payment.errors, :status => :unprocessable_entity }
      end
    end
  end

  # DELETE /remote_payments/1
  # DELETE /remote_payments/1.json
  def destroy
    @remote_payment = RemotePayment.find(params[:id])
    @remote_payment.destroy

    respond_to do |format|
      format.html { redirect_to remote_payments_url }
      format.json { head :ok }
    end
  end
end
