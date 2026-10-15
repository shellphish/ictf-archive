class AdminController < ApplicationController

  before_filter :login_required
  before_filter :admin_required

  def index
    list
    render :action => 'list'
  end

  # GETs should be safe (see http://www.w3.org/2001/tag/doc/whenToUseGet.html)
  verify :method => :post, :only => [ :destroy, :create, :update ],
         :redirect_to => { :action => :list }

  def list
    @deposit_pages, @deposits = paginate :deposits, :per_page => 10
  end

  def show
    @deposit = Deposit.find(params[:id])
  end

  def new
    @deposit = Deposit.new
  end

  def create
    @deposit = Deposit.new(params[:deposit])
    if @deposit.save
      flash[:notice] = 'Deposit was successfully created.'
      redirect_to :action => 'list'
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

  def destroy
    Deposit.find(params[:id]).destroy
    redirect_to :action => 'list'
  end


  private 

    def admin_required
    
        if not current_user.admin
            flash[:error] = 'You do not have access to the admin interface!'
            redirect_to :controller => 'session', :action => 'login'
        end

    end


end
