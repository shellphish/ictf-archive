class AddTokenToRemotePayment < ActiveRecord::Migration
  def change
    change_table :remote_payments do |t|
      t.string :token
    end
  end
end
