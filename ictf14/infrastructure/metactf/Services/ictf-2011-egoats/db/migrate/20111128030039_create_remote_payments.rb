class CreateRemotePayments < ActiveRecord::Migration
  def change
    create_table :remote_payments do |t|

      t.timestamps
    end
  end
end
