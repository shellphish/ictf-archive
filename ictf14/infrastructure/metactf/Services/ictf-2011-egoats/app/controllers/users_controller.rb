class UsersController < ApplicationController
  skip_before_filter :authenticate_user!

  def index
    @users = User.paginate(:page => params[:page]).all
  end

  def show
    @user = User.find(params[:id])
  end

  def me
    redirect_to current_user
  end

end
