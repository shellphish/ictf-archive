class UserHasManyRemotePayments < ActiveRecord::Migration
  def change
    change_table :remote_payments do |t|
      t.references :user
    end
  end
end
