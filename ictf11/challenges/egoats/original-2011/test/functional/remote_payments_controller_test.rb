require 'test_helper'

class RemotePaymentsControllerTest < ActionController::TestCase
  setup do
    @remote_payment = remote_payments(:one)
  end

  test "should get index" do
    get :index
    assert_response :success
    assert_not_nil assigns(:remote_payments)
  end

  test "should get new" do
    get :new
    assert_response :success
  end

  test "should create remote_payment" do
    assert_difference('RemotePayment.count') do
      post :create, :remote_payment => @remote_payment.attributes
    end

    assert_redirected_to remote_payment_path(assigns(:remote_payment))
  end

  test "should show remote_payment" do
    get :show, :id => @remote_payment.to_param
    assert_response :success
  end

  test "should get edit" do
    get :edit, :id => @remote_payment.to_param
    assert_response :success
  end

  test "should update remote_payment" do
    put :update, :id => @remote_payment.to_param, :remote_payment => @remote_payment.attributes
    assert_redirected_to remote_payment_path(assigns(:remote_payment))
  end

  test "should destroy remote_payment" do
    assert_difference('RemotePayment.count', -1) do
      delete :destroy, :id => @remote_payment.to_param
    end

    assert_redirected_to remote_payments_path
  end
end
