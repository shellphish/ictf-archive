class UserController < ApplicationController

  before_filter :login_required

  # GETs should be safe (see http://www.w3.org/2001/tag/doc/whenToUseGet.html)
  verify :method => :post, :only => [ :destroy, :create, :update ],
         :redirect_to => { :action => :list }

  def show
    if (params[:id].nil?)
        @user = User.find(current_user.id, :include => [:contacts, :deposits])
    else 
        @user = User.find(params[:id], :include => [:contacts, :deposits])
    end
  end


  def show_deposits
    @user = current_user
    page = (params[:page] ||= 1).to_i
    items_per_page = 5
    offset = (page - 1) * items_per_page
    @deposits = @user.deposits
    @deposit_pages = Paginator.new(self, @deposits.length, items_per_page, page)
    @deposits = @deposits[offset..(offset + items_per_page - 1)]
  end

  def list
    @user_pages, @users = paginate(:users, 
        :order => "users.login", 
        :per_page => 5,
        :include => "contacts")
  end

  #def new
  #  @user = User.new
  #end

  #def create
  #  @user = User.new(params[:user])
  #  if @user.save
  #    flash[:notice] = 'User was successfully created.'
  #    redirect_to :action => 'list'
  #  else
  #    render :action => 'new'
  #  end
  #end

  def edit
    @user = current_user
  end

  def update
    @user = current_user
    if @user.update_attributes(params[:user])
      flash[:notice] = 'User was successfully updated.'
      redirect_to :action => 'show', :id => @user
    else
      render :action => 'edit'
    end
  end

  def add_contact
    user = User.find(params[:id])
    user.contacts << current_user unless user.contacts.include? current_user

    redirect_to :action => 'list'
  end

  def remove_contact

    user = User.find(params[:id])
    user.contacts.delete current_user

    redirect_to :action => 'list'
  end

  def destroy
    current_user.destroy
    redirect_to :controller => 'welcome'
  end
end
